# app/main.py
import os
import json
import signal
import asyncio
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from multiprocessing import Process

from dotenv import load_dotenv

# imports del proyecto
from app.consumidores.whatsapp_consumer import main as start_consumer
from app.services.handlers.soporte_handler import SoporteHandler
from app.notifications.worker_file import start_polling_for_changes

load_dotenv()

logger = logging.getLogger("app.main")
logger.setLevel(logging.INFO)

# configuración
NUM_WORKERS = int(os.getenv("NUM_CONSUMERS", os.cpu_count() or 1))
consumer_processes: List[Process] = []
LOCK_FILE = Path("consumers.lock")

# lock para asegurar que sólo un proceso lance el worker de notificaciones
NOTIFICATION_LOCK_FILE = Path("notification.lock")

# referencia global del worker
notification_task: Optional[asyncio.Task] = None
# flag para saber si este proceso creó el notification_task (para limpiarlo)
_notification_task_created_here = False


def write_lock(pids: List[int]):
    try:
        with open(LOCK_FILE, "w") as f:
            json.dump({"pids": pids}, f)
    except Exception:
        logger.exception("write_lock fallo")


def read_lock() -> List[int]:
    if not LOCK_FILE.exists():
        return []
    try:
        with open(LOCK_FILE, "r") as f:
            data = json.load(f)
            return data.get("pids", [])
    except Exception:
        return []


def remove_lock():
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        logger.exception("remove_lock fallo")


def is_pid_running(pid: int) -> bool:
    try:
        # signal 0 no mata, solo comprueba existencia (POSIX & Windows compat)
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def write_notification_lock(pid: int):
    try:
        with open(NOTIFICATION_LOCK_FILE, "w") as f:
            json.dump({"pid": pid}, f)
    except Exception:
        logger.exception("write_notification_lock fallo")


def read_notification_lock() -> Optional[int]:
    if not NOTIFICATION_LOCK_FILE.exists():
        return None
    try:
        with open(NOTIFICATION_LOCK_FILE, "r") as f:
            data = json.load(f)
            return data.get("pid")
    except Exception:
        return None


def remove_notification_lock():
    try:
        if NOTIFICATION_LOCK_FILE.exists():
            NOTIFICATION_LOCK_FILE.unlink()
    except Exception:
        logger.exception("remove_notification_lock fallo")


def kill_old_consumers():
    pids = read_lock()
    for pid in pids:
        try:
            if is_pid_running(pid):
                os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
    remove_lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global consumer_processes, notification_task, _notification_task_created_here

    # 1️⃣ matar consumers antiguos
    kill_old_consumers()

    # 2️⃣ configurar webhook telegram (tu función existente)
    try:
        from app.controllers.telegram_controller import setup_telegram_webhook
        await setup_telegram_webhook()
    except Exception:
        logger.exception("Error en setup_telegram_webhook")

    # 3️⃣ Iniciar worker de notificaciones (UNA SOLA VEZ entre procesos)
    try:
        existing_pid = read_notification_lock()
        if existing_pid and is_pid_running(existing_pid):
            logger.info("Worker de notificaciones ya corre en PID %s — no se crea otro.", existing_pid)
            notification_task = None
            _notification_task_created_here = False
        else:
            # no hay worker activo: arrancamos uno en este proceso
            soporte_handler = SoporteHandler(root_handler=None)
            # crear la tarea background
            notification_task = asyncio.create_task(
                start_polling_for_changes(
                    soporte_handler._fetch_asignaciones,
                    poll_interval=int(os.getenv("NOTIFICATIONS_POLL_INTERVAL", "60"))
                )
            )
            write_notification_lock(os.getpid())
            _notification_task_created_here = True
            logger.info("Worker de notificaciones iniciado por PID %s", os.getpid())
    except Exception:
        logger.exception("Error iniciando worker de notificaciones")

    # 4️⃣ iniciar consumers de whatsapp (process pool)
    try:
        if not consumer_processes:
            pids = []
            for _ in range(NUM_WORKERS):
                p = Process(target=start_consumer, daemon=True)
                p.start()
                consumer_processes.append(p)
                pids.append(p.pid)
            write_lock(pids)
            logger.info("Iniciados %s consumers (PID list saved).", len(pids))
    except Exception:
        logger.exception("Error iniciando consumers")

    yield

    # ---------------------------
    # CLEANUP ordenado al apagar
    # ---------------------------
    # cancelar notification_task solo si fue creado por este proceso
    try:
        if _notification_task_created_here and notification_task:
            logger.info("Cancelando notification_task creada por este proceso...")
            notification_task.cancel()
            try:
                await notification_task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("Error esperando notification_task cancelado")
            remove_notification_lock()
    except Exception:
        logger.exception("Error limpiando notification_task")

    # detener consumers locales
    stopped = 0
    for p in consumer_processes:
        try:
            if p.is_alive():
                p.terminate()
                p.join(timeout=2)
                stopped += 1
        except Exception:
            logger.exception("Error deteniendo consumer")
    consumer_processes.clear()
    remove_lock()

    logger.info("Lifespan cleanup completado.")


app = FastAPI(lifespan=lifespan)

# Middlewares / CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static + routers (asegúrate que `templates` y rutas existen)
try:
    from app.config import templates  # noqa: F401
except Exception:
    logger.debug("No se pudo importar templates (posible entorno de test)")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Rutas principales
try:
    from app.routes.webhook_routes import router as webhook_router
    from app.routes.routes import router as mongo_router
    app.include_router(webhook_router)
    app.include_router(mongo_router)
except Exception:
    logger.exception("Error incluyendo routers principales")

# ---------------------------
# ADMINISTRACIÓN DE CONSUMERS
# ---------------------------
admin_router = APIRouter()


@admin_router.post("/admin/consumer/iniciar", response_class=JSONResponse)
async def iniciar_consumidor():
    global consumer_processes
    started = 0

    if not consumer_processes:
        for _ in range(NUM_WORKERS):
            p = Process(target=start_consumer, daemon=True)
            p.start()
            consumer_processes.append(p)
            started += 1
        # actualizar lock con PIDs actuales
        pids = [p.pid for p in consumer_processes if p.pid]
        write_lock(pids)
        return {"status": f"started {started} workers"}

    for i, p in enumerate(consumer_processes):
        if not p.is_alive():
            new_p = Process(target=start_consumer, daemon=True)
            new_p.start()
            consumer_processes[i] = new_p
            started += 1

    if started:
        pids = [p.pid for p in consumer_processes if p.pid]
        write_lock(pids)
        return {"status": f"restarted {started} workers"}

    return {"status": "already running"}


@admin_router.post("/admin/consumer/detener", response_class=JSONResponse)
async def detener_consumidor():
    global consumer_processes
    stopped = 0

    for p in consumer_processes:
        try:
            if p.is_alive():
                p.terminate()
                p.join()
                stopped += 1
        except Exception:
            logger.exception("Error terminando consumer")
    consumer_processes.clear()
    remove_lock()

    if stopped:
        return {"status": f"stopped {stopped} workers"}

    return {"status": "not running"}


app.include_router(admin_router)

# ---------------------------
# RUTAS TELEGRAM
# ---------------------------
try:
    from app.routes.telegram_routes import router as telegram_router
    app.include_router(telegram_router)
except Exception:
    logger.exception("Error incluyendo rutas de Telegram")


if __name__ == "__main__":
    # Nota: en desarrollo puedes usar reload=True, pero en producción NO uses --reload
    # porque uvicorn --reload crea procesos secundarios y puede duplicar tareas background.
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "80")),
        reload=bool(os.getenv("DEV_RELOAD", "True") == "True"),  # set DEV_RELOAD=False en prod
    )
