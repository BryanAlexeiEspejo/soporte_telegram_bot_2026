# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from app.services.feedback.feedback_repo import _get_collection, create_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])

# ----------------------------
# MODELO PARA SWAGGER
# ----------------------------
class FeedbackIn(BaseModel):
    user_id: str = Field(..., description="ID del usuario (WhatsApp)")
    user_name: Optional[str] = Field(None, description="Nombre del usuario")
    question: Optional[str] = Field(None, description="Pregunta hecha por el usuario")
    answer: Optional[str] = Field(None, description="Respuesta generada por el chatbot")
    useful: Optional[bool] = Field(None, description="Si la respuesta fue útil o no")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Calificación 1 a 5")
    feedback_question: Optional[str] = Field(None, description="Pregunta adicional si no fue útil")
    conversation_id: Optional[str] = Field(None, description="ID de conversación de WhatsApp")


class FeedbackOut(FeedbackIn):
    id: str = Field(..., description="ID del documento creado en MongoDB")
    timestamp: str = Field(..., description="Fecha en formato ISO")


# ----------------------------
# EJEMPLO PARA SWAGGER UI
# ----------------------------

example_payload = {
    "user_id": "59162411568",
    "user_name": "Juan Pérez",
    "question": "ciudadano",
    "answer": "Respuesta generada por el chatbot...",
    "useful": True,
    "rating": 4,
    "feedback_question": None,
    "conversation_id": "wamid.XXXYYYZZZ"
}

# ----------------------------
#     ENDPOINTS
# ----------------------------

@router.post(
    "/",
    summary="Crear feedback manual (para pruebas)",
    response_model=FeedbackOut
)
def create(f: FeedbackIn = Body(..., example=example_payload)):
    """
    Crea un registro de feedback manual en MongoDB.
    Útil para pruebas desde Swagger UI.
    """
    try:
        new_id = create_feedback(f.dict())
        col = _get_collection()
        doc = col.find_one({"_id": col._client.get_default_database().get_collection("feedback_chatbot").find_one({"_id": new_id})})

        return FeedbackOut(
            id=new_id,
            timestamp=str(f.dict().get("timestamp")),
            **f.dict()
        )

    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/", summary="Listar feedback", response_model=List[Dict[str, Any]])
def list_feedback(limit: int = Query(50, ge=1, le=500)):
    """
    Lista los últimos documentos de la colección feedback_chatbot.
    """
    col = _get_collection()
    docs = list(col.find().sort("timestamp", -1).limit(limit))

    for d in docs:
        d["id"] = str(d.pop("_id"))
        if "timestamp" in d and hasattr(d["timestamp"], "isoformat"):
            d["timestamp"] = d["timestamp"].isoformat()
    return docs
