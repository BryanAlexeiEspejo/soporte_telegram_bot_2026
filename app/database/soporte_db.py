# app/database/soporte_db.py
# -*- coding: utf-8 -*-
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
ENV = os.getenv("ENV", "prod")

# Crear cliente motor async
client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))

DB_NAME = "parqueos_test" if ENV == "local" else "parqueos"
db = client[DB_NAME]

print(f"🟢 MongoDB usando base: {DB_NAME}")

# -----------------------
# Colecciones
# -----------------------
conversaciones = db["conversaciones"]
mensajes_procesados = db["mensajes_procesados"]  # corregido typo
soporte26 = db["soporte26"]                      # antes historial26, ahora soporte26
telegram_users = db["telegram_users"]            # colección para usuarios de Telegram

# =========================
# ESTADO DE USUARIO
# =========================
async def get_estado_usuario(numero: str) -> dict:
    """
    Devuelve el documento de la colección 'conversaciones' para el número dado.
    """
    doc = await conversaciones.find_one({"numero": str(numero)})
    return doc or {}

async def set_estado_usuario(numero: str, estado: dict):
    """
    Actualiza el estado del usuario de forma segura:
    - Evita conflictos de 'updated_at' eliminándolo si viene en 'estado'
    - Usa $currentDate para que Mongo gestione 'updated_at'
    - Usa $setOnInsert para created_at cuando se crea el documento
    """
    now = datetime.utcnow()

    # Evitar conflicto: si caller pasó updated_at, lo eliminamos
    safe_estado = {k: v for k, v in (estado or {}).items() if k != "updated_at" and k != "_id"}

    update = {
        "$set": {**safe_estado},
        "$currentDate": {"updated_at": True},
        "$setOnInsert": {"created_at": now, "numero": str(numero)}
    }

    await conversaciones.update_one({"numero": str(numero)}, update, upsert=True)

# =========================
# MENSAJES PROCESADOS
# =========================
async def buscar_mensaje_procesado(mensaje_id: str) -> bool:
    doc = await mensajes_procesados.find_one({"mensaje_id": mensaje_id})
    return doc is not None

async def registrar_mensaje_procesado(mensaje_id: str):
    await mensajes_procesados.insert_one({
        "mensaje_id": mensaje_id,
        "fecha_hora": datetime.utcnow()
    })

# =========================
# REGISTRO DE HISTORIAL -> colección 'soporte26'
# =========================
async def registrar_historial(
    origen: str,      # "BOT" o "USUARIO"
    actor: str,       # "AMI", "WhatsApp", o nombre visible del usuario
    numero: str,
    texto: str
):
    """
    Inserta un registro en la colección soporte26 (antes historial26).
    """
    await soporte26.insert_one({
        "tipo": f"{origen} | {actor}",
        "actor": actor,
        "numero": str(numero),
        "mensaje": texto,
        "fecha_hora": datetime.utcnow()
    })

async def registrar_historial_telegram(
    message_type: str,  # "message", "callback", "command"
    user_id: int,
    username: str,
    first_name: str,
    text: str,
    chat_id: int = None
):
    """
    Registra historial específico para Telegram en soporte26.
    """
    await soporte26.insert_one({
        "tipo": f"TELEGRAM | {message_type.upper()}",
        "actor": f"{first_name} (@{username})" if username else first_name,
        "numero": str(user_id),
        "chat_id": chat_id or user_id,
        "mensaje": text,
        "telegram_data": {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "message_type": message_type
        },
        "fecha_hora": datetime.utcnow()
    })

# =========================
# TELEGRAM USERS (unificado)
# =========================
async def get_or_create_telegram_user(
    telegram_id: int,
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    chat_id: int = None
) -> dict:
    """
    Busca un usuario por telegram_id; si no existe lo crea.
    Retorna el documento del usuario (con _id si fue insertado).
    """
    user = await telegram_users.find_one({"telegram_id": telegram_id})
    
    if not user:
        user_data = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "chat_id": chat_id or telegram_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0
        }
        result = await telegram_users.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        # Devolver la estructura con _id para coherencia
        return user_data

    # actualizar información si cambió
    update_data = {}
    if username and username != user.get("username"):
        update_data["username"] = username
    if first_name and first_name != user.get("first_name"):
        update_data["first_name"] = first_name
    if last_name and last_name != user.get("last_name"):
        update_data["last_name"] = last_name
    if chat_id and chat_id != user.get("chat_id"):
        update_data["chat_id"] = chat_id

    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await telegram_users.update_one({"telegram_id": telegram_id}, {"$set": update_data})
        user.update(update_data)

    # incrementar contador de mensajes (separado para evitar conflictos)
    await telegram_users.update_one({"telegram_id": telegram_id}, {"$inc": {"message_count": 1}})
    # devolver la versión más actualizada
    return await telegram_users.find_one({"telegram_id": telegram_id})

async def get_telegram_user(telegram_id: int) -> dict:
    return await telegram_users.find_one({"telegram_id": telegram_id})

async def update_telegram_user(telegram_id: int, update_data: dict) -> bool:
    update_data = {k: v for k, v in update_data.items() if k != "_id"}
    update_data["updated_at"] = datetime.utcnow()
    result = await telegram_users.update_one({"telegram_id": telegram_id}, {"$set": update_data})
    return (result.modified_count if hasattr(result, "modified_count") else getattr(result, "modified_count", 0)) > 0

async def get_all_telegram_users(limit: int = 100) -> list:
    cursor = telegram_users.find().sort("updated_at", -1).limit(limit)
    return await cursor.to_list(length=limit)

# =========================
# UTILIDADES
# =========================
async def get_hora_mongo():
    # isMaster es deprecated en algunas versiones, pero lo mantenemos por compatibilidad
    try:
        result = await db.command("isMaster")
        return result.get("localTime")
    except Exception:
        # fallback: devolver ahora UTC
        return datetime.utcnow()

# =========================
# FUNCIONES AUXILIARES DE ESTADÍSTICAS
# =========================
async def get_telegram_stats() -> dict:
    """Obtiene estadísticas de usuarios de Telegram"""
    total_users = await telegram_users.count_documents({})
    # Usuarios activos desde medianoche UTC del día actual
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    active_users = await telegram_users.count_documents({"updated_at": {"$gte": today_start}})

    top_user_cursor = telegram_users.find().sort("message_count", -1).limit(1)
    top_user_list = await top_user_cursor.to_list(length=1)

    return {
        "total_users": total_users,
        "active_today": active_users,
        "top_user": top_user_list[0] if top_user_list else None
    }

# =========================
# MIGRACIÓN: copiar conversaciones a telegram_users (opcional)
# =========================
async def migrate_existing_telegram_users():
    """
    Migrar usuarios de 'conversaciones' a 'telegram_users' (opcional).
    """
    cursor = conversaciones.find({
        "numero": {"$regex": "^[0-9]+$", "$type": "string"},
        "numero": {"$not": {"$regex": "^591"}}  # opcional: filtrar números
    })

    migrated_count = 0
    async for doc in cursor:
        numero = doc.get("numero")
        if numero and numero.isdigit():
            telegram_id = int(numero)
            existing = await telegram_users.find_one({"telegram_id": telegram_id})
            if not existing:
                await telegram_users.insert_one({
                    "telegram_id": telegram_id,
                    "username": "",
                    "first_name": f"Usuario_{telegram_id}",
                    "last_name": "",
                    "chat_id": telegram_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "message_count": 0,
                    "migrated": True
                })
                migrated_count += 1

    if migrated_count:
        print(f"✅ Migrados {migrated_count} usuarios a telegram_users")
    return migrated_count
