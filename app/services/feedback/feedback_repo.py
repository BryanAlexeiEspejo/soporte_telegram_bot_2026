# -*- coding: utf-8 -*-
import os
import datetime as _dt
from typing import Dict, Any
from pymongo import MongoClient, errors
from bson import ObjectId

_client = None
_coll = None


def _get_collection():
    global _client, _coll
    if _coll is not None:
        return _coll

    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    dbn = os.getenv("MONGO_DB", "ami")
    coll_name = os.getenv("FEEDBACK_COLLECTION", "feedback_chatbot")

    try:
        _client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            retryWrites=True,
        )

        # Validar conexión
        _client.admin.command("ping")

        # Seleccionar DB y colección
        _coll = _client[dbn][coll_name]

        # Crear índices
        _coll.create_index("user_id")
        _coll.create_index("timestamp")
        _coll.create_index("conversation_id")

        return _coll

    except errors.PyMongoError as e:
        raise RuntimeError(f" Error conectando a MongoDB: {e}")


def create_feedback(doc: Dict[str, Any]) -> str:
    """Inserta feedback con timestamp automático"""
    col = _get_collection()
    doc = dict(doc or {})
    doc.setdefault("timestamp", _dt.datetime.utcnow())
    result = col.insert_one(doc)
    return str(result.inserted_id)


def update_feedback(feedback_id: str, updates: Dict[str, Any]) -> None:
    """Actualiza un documento existente de feedback"""
    col = _get_collection()
    col.update_one({"_id": ObjectId(feedback_id)}, {"$set": dict(updates or {})})
