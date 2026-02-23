# app/services/handlers/catastro/D_3_info_catastro_3.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

async def manejar_info_catastro_3(numero: str) -> List[Dict]:
    # 🧾 Cuerpo con las preguntas 1–8 “tal cual”
    cuerpo = (
        "------------------------------\n"
        "*Registro y documentación catastral*\n"
        "1. ¿Qué tipos de bienes inmuebles están sujetos a registro catastral?\n"
        "2. ¿Qué es un levantamiento catastral?\n"
        "3. ¿Qué es el código catastral y para qué sirve?\n"
        "4. ¿Qué hago si pierdo mi código catastral?\n"
        "5. ¿Qué es un certificado de no existencia catastral?\n"
        "6. ¿Cómo puedo solicitar un certificado de no existencia catastral?\n"
        "7. ¿Cómo puedo saber si mi inmueble está registrado como bien municipal?\n"
        "8. ¿Qué documentos necesito para solicitar copias simples o legalizadas en el archivo de catastro?\n"
        "------------------------------\n"
        "Selecciona una opción:"
    )

    q1 = "¿Qué tipos de bienes inmuebles están sujetos a registro catastral?"
    q2 = "¿Qué es un levantamiento catastral?"
    q3 = "¿Qué es el código catastral y para qué sirve?"
    q4 = "¿Qué hago si pierdo mi código catastral?"
    q5 = "¿Qué es un certificado de no existencia catastral?"
    q6 = "¿Cómo puedo solicitar un certificado de no existencia catastral?"
    q7 = "¿Cómo puedo saber si mi inmueble está registrado como bien municipal?"
    q8 = "¿Qué documentos necesito para solicitar copias simples o legalizadas en el archivo de catastro?"

    # 8 preguntas + “Más (9–12)” + “Inicio” = 10 filas total ✅
    secciones = [{
        "title": "Opciones",
        "rows": [
            {"id": "q-catastro-3-1",  "title": "1", "description": _short(q1)},
            {"id": "q-catastro-3-2",  "title": "2", "description": _short(q2)},
            {"id": "q-catastro-3-3",  "title": "3", "description": _short(q3)},
            {"id": "q-catastro-3-4",  "title": "4", "description": _short(q4)},
            {"id": "q-catastro-3-5",  "title": "5", "description": _short(q5)},
            {"id": "q-catastro-3-6",  "title": "6", "description": _short(q6)},
            {"id": "q-catastro-3-7",  "title": "7", "description": _short(q7)},
            {"id": "q-catastro-3-8",  "title": "8", "description": _short(q8)},
            {"id": "info-catastro-3-p2", "title": "➡️ Más (9–12)", "description": "Ver más preguntas"},
            {"id": "catastro-d", "title": "🏠 Volver", "description": "Volver a preguntas"},
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Ver preguntas"
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "info-catastro-3"})
    return [payload]
