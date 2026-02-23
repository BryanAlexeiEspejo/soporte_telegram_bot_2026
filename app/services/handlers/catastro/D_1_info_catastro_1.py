# app/services/handlers/catastro/D_1_info_catastro_1.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

# ✅ LIST con una sola sección (1–10) y las preguntas "tal cual" en la descripción.
async def manejar_info_catastro_1(numero: str) -> List[Dict]:
    cuerpo = (
        "📘 *Información general sobre el catastro*\n"
        "-----------------------------------------\n"
        "1) ¿Qué es el catastro municipal?\n"
        "2) ¿Qué es un bien inmueble o predio?\n"
        "3) ¿Qué es una ficha/formulario/etc. catastral?\n"
        "4) ¿Qué es la georreferenciación en el catastro?\n"
        "5) ¿Qué es el avalúo catastral?\n"
        "6) ¿Qué es un conflicto de sobreposición catastral?\n"
        "7) ¿Qué diferencia hay entre un catastro urbano y un catastro rural?\n"
        "8) ¿Qué son los bienes de dominio municipal?\n"
        "9) ¿Cuáles son los beneficios de tener un inmueble registrado en el catastro?\n"
        "10) ¿Cuál es la importancia de tener un Certificado de Registro Catastral?\n\n"
        "Selecciona una opción:"
    )

    q1  = "¿Qué es el catastro municipal?"
    q2  = "¿Qué es un bien inmueble o predio?"
    q3  = "¿Qué es una ficha/formulario/etc. catastral?"
    q4  = "¿Qué es la georreferenciación en el catastro?"
    q5  = "¿Qué es el avalúo catastral?"
    q6  = "¿Qué es un conflicto de sobreposición catastral?"
    q7  = "¿Qué diferencia hay entre un catastro urbano y un catastro rural?"
    q8  = "¿Qué son los bienes de dominio municipal?"
    q9  = "¿Cuáles son los beneficios de tener un inmueble registrado en el catastro?"
    q10 = "¿Cuál es la importancia de tener un Certificado de Registro Catastral?"

    secciones = [{
        "title": "Preguntas (1–10)",
        "rows": [
            {"id": "q-catastro-1",  "title": "1",  "description": _short(q1)},
            {"id": "q-catastro-2",  "title": "2",  "description": _short(q2)},
            {"id": "q-catastro-3",  "title": "3",  "description": _short(q3)},
            {"id": "q-catastro-4",  "title": "4",  "description": _short(q4)},
            {"id": "q-catastro-5",  "title": "5",  "description": _short(q5)},
            {"id": "q-catastro-6",  "title": "6",  "description": _short(q6)},
            {"id": "q-catastro-7",  "title": "7",  "description": _short(q7)},
            {"id": "q-catastro-8",  "title": "8",  "description": _short(q8)},
            {"id": "q-catastro-9",  "title": "9",  "description": _short(q9)},
            {"id": "q-catastro-10", "title": "10", "description": _short(q10)},
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,          # Texto principal con las 10 preguntas completas
        opciones=secciones,     # 1 sección
        header_text="",
        footer_text="",
        button_text="Ver preguntas"   # ≤20
    )

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "info-catastro-1"
    })

    return [payload]
