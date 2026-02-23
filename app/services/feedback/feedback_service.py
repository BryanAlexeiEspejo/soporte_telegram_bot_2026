import os
from datetime import datetime
from typing import Dict, Any, Optional
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "chatbot_db")

# Cliente MongoDB (singleton)
_mongo_client = None
_mongo_db = None

def get_mongo_db():
    """Obtiene la conexión a MongoDB (singleton)"""
    global _mongo_client, _mongo_db
    if _mongo_db is None:
        _mongo_client = MongoClient(MONGO_URI)
        _mongo_db = _mongo_client[MONGO_DB]
    return _mongo_db

def start_feedback_record(
    user_id: str,
    user_name: str,
    question: str,
    answer: str,
    conversation_id: str = None,
    flow: str = "chatbot",
    flow_id: str = None
) -> str:
    """
    Crea un registro inicial de feedback en MongoDB.

    Args:
        user_id: ID del usuario (número de teléfono)
        user_name: Nombre del usuario
        question: Pregunta original del usuario
        answer: Respuesta generada por el chatbot
        conversation_id: ID de la conversación de WhatsApp
        flow: Flujo desde el cual llegó el feedback (ej: 'tramites', 'ciudadano', 'catastro', 'chatbot')
        flow_id: ID interno del flujo (si aplica)

    Returns:
        str: ID del documento creado
    """
    try:
        db = get_mongo_db()
        collection = db['feedback_chatbot']

        feedback_doc = {
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow(),
            "question": question,
            "answer": answer,
            "conversation_id": conversation_id,

            # NUEVOS CAMPOS PARA MULTI-FLOW
            "flow": flow,
            "flow_id": flow_id,

            "useful": None,
            "rating": None,
            "feedback_question": None,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": None
        }

        result = collection.insert_one(feedback_doc)
        feedback_id = str(result.inserted_id)

        print(f"✅ Feedback record created: {feedback_id}")
        return feedback_id

    except Exception as e:
        print(f"❌ Error creating feedback record: {e}")
        import traceback
        traceback.print_exc()
        raise

def set_useful(feedback_id: str, useful: bool) -> bool:
    """
    Actualiza si la respuesta fue útil
    
    Args:
        feedback_id: ID del documento de feedback
        useful: True si fue útil, False si no
    
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        db = get_mongo_db()
        collection = db['feedback_chatbot']
        
        result = collection.update_one(
            {"_id": ObjectId(feedback_id)},
            {
                "$set": {
                    "useful": useful,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        success = result.modified_count > 0
        print(f"{'✅' if success else '⚠️'} Updated useful={useful} for feedback {feedback_id}")
        return success
    
    except Exception as e:
        print(f"❌ Error updating useful: {e}")
        import traceback
        traceback.print_exc()
        return False

def set_rating(feedback_id: str, rating: int) -> bool:
    """
    Actualiza la calificación del usuario
    
    Args:
        feedback_id: ID del documento de feedback
        rating: Calificación de 1 a 5
    
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        if not (1 <= rating <= 5):
            print(f"⚠️ Invalid rating: {rating}. Must be between 1 and 5")
            return False
        
        db = get_mongo_db()
        collection = db['feedback_chatbot']
        
        result = collection.update_one(
            {"_id": ObjectId(feedback_id)},
            {
                "$set": {
                    "rating": rating,
                    "status": "completed",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        success = result.modified_count > 0
        print(f"{'✅' if success else '⚠️'} Updated rating={rating} for feedback {feedback_id}")
        return success
    
    except Exception as e:
        print(f"❌ Error updating rating: {e}")
        import traceback
        traceback.print_exc()
        return False

def set_feedback_question(feedback_id: str, feedback_question: str) -> bool:
    """
    Actualiza la pregunta/comentario adicional del usuario
    
    Args:
        feedback_id: ID del documento de feedback
        feedback_question: Pregunta o comentario del usuario
    
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        db = get_mongo_db()
        collection = db['feedback_chatbot']
        
        result = collection.update_one(
            {"_id": ObjectId(feedback_id)},
            {
                "$set": {
                    "feedback_question": feedback_question,
                    "status": "completed",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        success = result.modified_count > 0
        print(f"{'✅' if success else '⚠️'} Updated feedback_question for feedback {feedback_id}")
        return success
    
    except Exception as e:
        print(f"❌ Error updating feedback_question: {e}")
        import traceback
        traceback.print_exc()
        return False

def build_useful_prompt(numero: str) -> Dict[str, Any]:
    """
    Construye el mensaje de WhatsApp preguntando si fue útil
    
    Args:
        numero: Número de teléfono del destinatario
    
    Returns:
        Dict con el payload de WhatsApp
    """
    return {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "¿La información que te di te fue útil?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "fb_yes",
                            "title": "Sí ✅"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "fb_no",
                            "title": "No ❌"
                        }
                    }
                ]
            }
        }
    }

def build_rating_prompt(numero: str) -> Dict[str, Any]:
    """
    Construye el mensaje de WhatsApp pidiendo calificación
    
    Args:
        numero: Número de teléfono del destinatario
    
    Returns:
        Dict con el payload de WhatsApp
    """
    return {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "¡Genial! ¿Podrías calificar la respuesta del 1 al 5?\n\n1 = Nada útil\n5 = Muy útil"
            },
            "action": {
                "button": "Calificar ⭐",
                "sections": [
                    {
                        "title": "Calificación",
                        "rows": [
                            {
                                "id": "fb_rating_5",
                                "title": "⭐⭐⭐⭐⭐ (5)",
                                "description": "Excelente"
                            },
                            {
                                "id": "fb_rating_4",
                                "title": "⭐⭐⭐⭐ (4)",
                                "description": "Muy bueno"
                            },
                            {
                                "id": "fb_rating_3",
                                "title": "⭐⭐⭐ (3)",
                                "description": "Bueno"
                            },
                            {
                                "id": "fb_rating_2",
                                "title": "⭐⭐ (2)",
                                "description": "Regular"
                            },
                            {
                                "id": "fb_rating_1",
                                "title": "⭐ (1)",
                                "description": "Malo"
                            }
                        ]
                    }
                ]
            }
        }
    }

def ask_free_question(numero: str) -> Dict[str, Any]:
    """
    Construye el mensaje pidiendo una pregunta adicional
    
    Args:
        numero: Número de teléfono del destinatario
    
    Returns:
        Dict con el payload de WhatsApp
    """
    return {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {
            "body": "Lamento no haber sido de ayuda. 😔\n\nPor favor, envíame tu pregunta o comentario para que podamos mejorar:"
        }
    }

def thanks_text(numero: str, mensaje: str = None) -> Dict[str, Any]:
    """
    Construye mensaje de agradecimiento
    
    Args:
        numero: Número de teléfono del destinatario
        mensaje: Mensaje personalizado (opcional)
    
    Returns:
        Dict con el payload de WhatsApp
    """
    if mensaje is None:
        mensaje = "¡Gracias por tu feedback! 😊 Esto nos ayuda a mejorar.\n\n¿En qué más puedo ayudarte?"
    
    return {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje
        }
    }

def get_feedback_stats(user_id: str = None, days: int = 30) -> Dict[str, Any]:
    """
    Obtiene estadísticas de feedback
    
    Args:
        user_id: Filtrar por usuario específico (opcional)
        days: Número de días hacia atrás para consultar
    
    Returns:
        Dict con estadísticas
    """
    try:
        db = get_mongo_db()
        collection = db['feedback_chatbot']
        
        # Construir filtro
        from datetime import timedelta
        date_filter = datetime.utcnow() - timedelta(days=days)
        query = {"timestamp": {"$gte": date_filter}}
        
        if user_id:
            query["user_id"] = user_id
        
        # Obtener todos los registros
        feedbacks = list(collection.find(query))
        
        # Calcular estadísticas
        total = len(feedbacks)
        useful_count = sum(1 for f in feedbacks if f.get("useful") == True)
        not_useful_count = sum(1 for f in feedbacks if f.get("useful") == False)
        
        ratings = [f.get("rating") for f in feedbacks if f.get("rating") is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        comments = [f.get("feedback_question") for f in feedbacks if f.get("feedback_question")]
        
        stats = {
            "total_feedback": total,
            "useful": useful_count,
            "not_useful": not_useful_count,
            "avg_rating": round(avg_rating, 2),
            "total_ratings": len(ratings),
            "total_comments": len(comments),
            "period_days": days
        }
        
        print(f"📊 Feedback stats: {stats}")
        return stats
    
    except Exception as e:
        print(f" Error getting feedback stats: {e}")
        return {}