# -*- coding: utf-8 -*-
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
ENV = os.getenv("ENV", "prod")

client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi("1"))

DB_NAME = "parqueos_test" if ENV == "local" else "parqueos"
db = client[DB_NAME]

print(f"🟢 MongoDB usando base: {DB_NAME}")

# =========================
# COLECCIONES
# =========================
conversaciones = db["conversaciones"]
mensajes_procesados = db["mensyajes_procesados"]
historial26 = db["historial27"]
telegram_users = db["telegram_users"]

# =========================
# ESTADO DE USUARIO
# =========================
async def get_estado_usuario(numero: str) -> dict:
    return await conversaciones.find_one({"numero": numero})

async def set_estado_usuario(numero: str, estado: dict):
    """
    Actualiza estado del usuario sin conflicto de updated_at
    """
    estado_limpio = dict(estado)
    estado_limpio.pop("updated_at", None)
    estado_limpio.pop("created_at", None)

    await conversaciones.update_one(
        {"numero": numero},
        {
            "$set": {
                **estado_limpio,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )

# =========================
# MENSAJES PROCESADOS
# =========================
async def buscar_mensaje_procesado(mensaje_id: str) -> bool:
    return await mensajes_procesados.find_one({"mensaje_id": mensaje_id}) is not None

async def registrar_mensaje_procesado(mensaje_id: str):
    await mensajes_procesados.insert_one({
        "mensaje_id": mensaje_id,
        "fecha_hora": datetime.utcnow()
    })

# =========================
# TELEGRAM USERS
# =========================
async def get_or_create_telegram_user(
    telegram_id: int,
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    chat_id: int = None
) -> dict:
    user = await telegram_users.find_one({"telegram_id": telegram_id})

    if not user:
        user = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "chat_id": chat_id or telegram_id,
            "message_count": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await telegram_users.insert_one(user)
        print(f"✅ Usuario Telegram creado: {telegram_id}")
        return user

    update_data = {"updated_at": datetime.utcnow()}
    changed = False

    for field, value in {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "chat_id": chat_id
    }.items():
        if value and value != user.get(field):
            update_data[field] = value
            changed = True

    update_ops = {"$inc": {"message_count": 1}}
    if changed:
        update_ops["$set"] = update_data
    else:
        update_ops["$set"] = {"updated_at": datetime.utcnow()}

    await telegram_users.update_one(
        {"telegram_id": telegram_id},
        update_ops
    )

    user.update(update_data)
    user["message_count"] = user.get("message_count", 0) + 1
    return user

async def get_telegram_user(telegram_id: int) -> dict:
    return await telegram_users.find_one({"telegram_id": telegram_id})

# =========================
# HISTORIAL
# =========================
async def registrar_historial(
    origen: str,
    actor: str,
    numero: str,
    texto: str
):
    await historial26.insert_one({
        "tipo": f"{origen} | {actor}",
        "actor": actor,
        "numero": numero,
        "mensaje": texto,
        "fecha_hora": datetime.utcnow()
    })

async def registrar_historial_telegram(
    message_type: str,
    user_id: int,
    username: str,
    first_name: str,
    text: str,
    chat_id: int = None
):
    await historial26.insert_one({
        "tipo": f"TELEGRAM | {message_type.upper()}",
        "actor": f"{first_name} (@{username})" if username else first_name,
        "numero": str(user_id),
        "chat_id": chat_id or user_id,
        "mensaje": text,
        "fecha_hora": datetime.utcnow()
    })

# =========================
# ESTADÍSTICAS
# =========================
async def get_telegram_stats() -> dict:
    total = await telegram_users.count_documents({})
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    activos = await telegram_users.count_documents({
        "updated_at": {"$gte": hoy}
    })

    top = await telegram_users.find().sort("message_count", -1).limit(1).to_list(1)

    return {
        "total_users": total,
        "active_today": activos,
        "top_user": top[0] if top else None
    }
async def get_hora_mongo():
    """
    Devuelve la hora del servidor MongoDB
    """
    try:
        result = await db.command("hello")
        return result.get("localTime", datetime.utcnow())
    except Exception:
        return datetime.utcnow()