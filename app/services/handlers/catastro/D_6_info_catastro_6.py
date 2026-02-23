# app/services/handlers/catastro/D_6_info_catastro_6.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

# ✅ LIST con secciones (Preguntas + Navegación)
async def manejar_info_catastro_6(numero: str) -> List[Dict]:
    # Cuerpo con las preguntas “tal cual”
    cuerpo = (
        "------------------------------\n"
        "*Trámites y procedimientos*\n"
        "1. ¿Qué debo hacer si hay una sobreposición de mi terreno con el de mi vecino?\n"
        "2. ¿Qué pasa si no registro mi inmueble en el catastro?\n"
        "3. ¿Cómo puedo cambiar el uso de suelo de mi propiedad?\n"
        "4. ¿Dónde se encuentra el área de archivo de catastro y cuál es su horario de atención?\n"
        "5. ¿Qué sucede si el documento que solicitó no está disponible en el archivo de catastro?\n"
        "6. ¿Qué alternativas tengo si necesito un documento catastral que no se encuentra en el archivo de la calle Potosí?\n"
        "7. ¿Cuál es y dónde consigo el último plano (AS BUILD) o último plano aprobado?\n"
        "------------------------------\n"
        "Selecciona una opción:"
    )

    q1 = "¿Qué debo hacer si hay una sobreposición de mi terreno con el de mi vecino?"
    q2 = "¿Qué pasa si no registro mi inmueble en el catastro?"
    q3 = "¿Cómo puedo cambiar el uso de suelo de mi propiedad?"
    q4 = "¿Dónde se encuentra el área de archivo de catastro y cuál es su horario de atención?"
    q5 = "¿Qué sucede si el documento que solicitó no está disponible en el archivo de catastro?"
    q6 = "¿Qué alternativas tengo si necesito un documento catastral que no se encuentra en el archivo de la calle Potosí?"
    q7 = "¿Cuál es y dónde consigo el último plano (AS BUILD) o último plano aprobado?"

    secciones = [
        {
            "title": "Preguntas (1–7)",
            "rows": [
                {"id": "q-catastro-6-1", "title": "1", "description": _short(q1)},
                {"id": "q-catastro-6-2", "title": "2", "description": _short(q2)},
                {"id": "q-catastro-6-3", "title": "3", "description": _short(q3)},
                {"id": "q-catastro-6-4", "title": "4", "description": _short(q4)},
                {"id": "q-catastro-6-5", "title": "5", "description": _short(q5)},
                {"id": "q-catastro-6-6", "title": "6", "description": _short(q6)},
                {"id": "q-catastro-6-7", "title": "7", "description": _short(q7)},
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

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "info-catastro-6"})
    return [payload]
