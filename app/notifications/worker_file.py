# worker_file.py
import os
import json
import tempfile
import asyncio
import logging
from typing import Callable, Awaitable, List, Dict, Optional

from app.notifications.subscriptions_file import (
    list_all_codes,
    get_subscribers_file,
)
from app.database.database import get_estado_usuario, set_estado_usuario
from app.services.utils.telegram_send import send_telegram_text

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("NOTIFICATIONS_LOG_LEVEL", "INFO"))

BASE_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(BASE_DIR, exist_ok=True)

LAST_SENT_FILE = os.path.join(BASE_DIR, "notifications_sent.json")
_FILE_LOCK = asyncio.Lock()

# Estados ampliados
INTEREST_STATES = {
    "DESIGNADO",
    "ATENDIDO",
    "EN VENTANILLA",
    "ACEPTADO",
    "REASIGNADO",
    "EN PROCESO",
}


def _normalize_state(raw: Optional[str]) -> str:
    if raw is None:
        return ""
    s = str(raw).strip().upper()
    s = s.replace("_", " ")
    s = s.replace("-", " ")
    s = " ".join(s.split())
    return s


def _ensure_file():
    if not os.path.exists(LAST_SENT_FILE):
        with open(LAST_SENT_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


async def _load_states() -> Dict[str, Dict[str, str]]:
    _ensure_file()
    async with _FILE_LOCK:
        try:
            with open(LAST_SENT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {}
                out = {}
                for code, mapping in data.items():
                    out[str(code)] = {str(k): str(v) for k, v in (mapping or {}).items()}
                return out
        except Exception:
            logger.exception("Error leyendo LAST_SENT_FILE")
            return {}


async def _save_states(data: Dict[str, Dict[str, str]]):
    async with _FILE_LOCK:
        fd, tmp_path = tempfile.mkstemp(dir=BASE_DIR)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, LAST_SENT_FILE)
        except Exception:
            logger.exception("Error escribiendo LAST_SENT_FILE")
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass


async def _get_last_state(codigo: str, chat_id: str) -> Optional[str]:
    data = await _load_states()
    return data.get(str(codigo), {}).get(str(chat_id))


async def _set_last_state(codigo: str, chat_id: str, estado: str):
    data = await _load_states()
    data.setdefault(str(codigo), {})[str(chat_id)] = str(estado)
    await _save_states(data)


# -------------------------
# Mensaje bonito con emojis
# -------------------------
def _friendly_message_for_state(codigo: str, last_state: Optional[str], nuevo_estado: str) -> str:
    saludo = "👋✨ ¡Hola!"

    if "ACEPTADO" in nuevo_estado:
        cuerpo = (
            "🟢✅ *Tu solicitud ha sido ACEPTADA.*\n\n"
            "📄 Tu trámite fue validado correctamente.\n"
            "🚀 Muy pronto continuará con el siguiente paso del proceso.\n"
            "🔔 Te avisaremos apenas haya novedades."
        )

    elif "REASIGNADO" in nuevo_estado:
        cuerpo = (
            "🔄👷 *Tu solicitud fue REASIGNADA.*\n\n"
            "📌 Ahora está siendo revisada por otro responsable.\n"
            "⏳ Muy pronto tendrás nuevas actualizaciones."
        )

    elif "EN PROCESO" in nuevo_estado:
        cuerpo = (
            "⚙️⏳ *Tu solicitud está EN PROCESO.*\n\n"
            "👨‍💼 Nuestro equipo ya está trabajando en tu trámite.\n"
            "✨ Muy pronto verás avances importantes."
        )

    elif "DESIGNADO" in nuevo_estado:
        cuerpo = (
            "🔔👷 *Tu solicitud fue DESIGNADA.*\n\n"
            "📋 Se asignó personal para atender tu trámite.\n"
            "⏳ Muy pronto recibirás información sobre el avance."
        )

    elif "VENTANILLA" in nuevo_estado:
        cuerpo = (
            "🪟📄 *Tu solicitud está en VENTANILLA.*\n\n"
            "🏢 Puedes pasar a recoger lo solicitado.\n"
            "🪪 No olvides llevar tu documento o comprobante.\n"
            "😊 ¡Te esperamos!"
        )

    elif "ATENDIDO" in nuevo_estado:
        cuerpo = (
            "🎉✅ *Tu solicitud fue ATENDIDA.*\n\n"
            "💙 Gracias por confiar en nosotros.\n"
            "📩 Si necesitas algo más, escribe 'soporte'."
        )

    else:
        cuerpo = (
            f"ℹ️ Estado actual: {nuevo_estado}\n\n"
            "🔔 Muy pronto podrías recibir más actualizaciones."
        )

    anterior = last_state or "—"

    texto = (
        f"{saludo}\n\n"
        f"📌 Código: {codigo}\n"
        f"📊 Estado anterior: {anterior}\n"
        f"🆕 Estado actual: {nuevo_estado}\n\n"
        f"{cuerpo}"
    )

    return texto


# ---------------------------------------------------------------------
# WORKER PRINCIPAL
# ---------------------------------------------------------------------
async def start_polling_for_changes(
    fetch_func: Callable[[], Awaitable[Optional[List[Dict]]]],
    poll_interval: int = 60
):
    logger.info("Worker de notificaciones iniciado (poll=%s s)", poll_interval)
    _ensure_file()

    while True:
        try:
            asignaciones = await fetch_func()
            if not asignaciones:
                await asyncio.sleep(poll_interval)
                continue

            index: Dict[str, Dict] = {}
            for a in asignaciones:
                codigo_raw = a.get("codigo_formulario") or a.get("codigo_form") or a.get("codigo")
                codigo = str(codigo_raw).strip() if codigo_raw is not None else ""
                if codigo:
                    index[codigo] = a

            codes = await list_all_codes()

            for codigo in codes:
                a = index.get(codigo)
                if not a:
                    continue

                raw_state = a.get("estado_formulario") or a.get("estado") or ""
                nuevo_estado = _normalize_state(raw_state)
                if not nuevo_estado:
                    continue

                interested = any(s in nuevo_estado for s in INTEREST_STATES)
                subscribers = await get_subscribers_file(codigo)
                if not subscribers:
                    continue

                if not interested:
                    for chat_pre in subscribers:
                        last_known = await _get_last_state(codigo, chat_pre)
                        if last_known is None:
                            await _set_last_state(codigo, chat_pre, nuevo_estado)
                            await set_estado_usuario(
                                chat_pre,
                                {**(await get_estado_usuario(chat_pre) or {}), "ultimo_estado": nuevo_estado}
                            )
                    continue

                for chat_id in subscribers:
                    last_state = await _get_last_state(codigo, chat_id)

                    if last_state is None:
                        await _set_last_state(codigo, chat_id, nuevo_estado)
                        await set_estado_usuario(
                            chat_id,
                            {**(await get_estado_usuario(chat_id) or {}), "ultimo_estado": nuevo_estado}
                        )
                        continue

                    if str(last_state) == nuevo_estado:
                        continue

                    friendly_text = _friendly_message_for_state(codigo, last_state, nuevo_estado)
                    await send_telegram_text(chat_id, friendly_text)

                    await _set_last_state(codigo, chat_id, nuevo_estado)
                    await set_estado_usuario(
                        chat_id,
                        {**(await get_estado_usuario(chat_id) or {}), "ultimo_estado": nuevo_estado}
                    )

        except Exception:
            logger.exception("Error general en worker")

        await asyncio.sleep(poll_interval)