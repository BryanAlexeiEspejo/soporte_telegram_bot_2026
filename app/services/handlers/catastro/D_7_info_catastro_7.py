# app/services/handlers/catastro/D_7_info_catastro_7.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

# ✅ LIST con secciones (Preguntas + Navegación)
async def manejar_info_catastro_7(numero: str) -> List[Dict]:
    # Cuerpo con las preguntas “tal cual”
    cuerpo = (
        "------------------------------\n"
        "*Requisitos y permisos*\n"
        "1. ¿Se necesita permiso para hacer un cuarto fuera de mi casa?\n"
        "2. ¿Qué documentos necesito para solicitar copias simples o legalizadas en el archivo de catastro?\n"
        "------------------------------\n"
        "Selecciona una opción:"
    )

    q1 = "¿Se necesita permiso para hacer un cuarto fuera de mi casa?"
    q2 = "¿Qué documentos necesito para solicitar copias simples o legalizadas en el archivo de catastro?"

    secciones = [
        {
            "title": "Preguntas (1–2)",
            "rows": [
                {"id": "q-catastro-7-1", "title": "1", "description": _short(q1)},
                {"id": "q-catastro-7-2", "title": "2", "description": _short(q2)},
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-d", "title": "⬅️ Menú anterior", "description": "Volver a preguntas frecuentes"},
                {"id": "inicio",     "title": "🏠 Inicio",        "description": "Volver al menú principal"},
            ],
        },
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Ver preguntas"
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "info-catastro-7"})
    return [payload]
