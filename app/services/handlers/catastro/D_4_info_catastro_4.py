# app/services/handlers/catastro/D_4_info_catastro_4.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

# ✅ LIST con secciones (Preguntas + Navegación)
async def manejar_info_catastro_4(numero: str) -> List[Dict]:
    # Cuerpo con las preguntas “tal cual”
    cuerpo = (
        "------------------------------\n"
        "*Actualización y corrección de datos*\n"
        "1. ¿Cómo se calcula el valor catastral de mi propiedad?\n"
        "2. ¿Cómo afecta el uso del suelo al valor catastral de mi propiedad?\n"
        "3. ¿Qué debo hacer si mi inmueble no está correctamente representado en la cartografía catastral?\n"
        "------------------------------\n"
        "Selecciona una opción:"
    )

    q1 = "¿Cómo se calcula el valor catastral de mi propiedad?"
    q2 = "¿Cómo afecta el uso del suelo al valor catastral de mi propiedad?"
    q3 = "¿Qué debo hacer si mi inmueble no está correctamente representado en la cartografía catastral?"

    secciones = [
        {
            "title": "Preguntas (1–3)",
            "rows": [
                {"id": "q-catastro-4-1", "title": "1", "description": _short(q1)},
                {"id": "q-catastro-4-2", "title": "2", "description": _short(q2)},
                {"id": "q-catastro-4-3", "title": "3", "description": _short(q3)},
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-d", "title": "⬅️ Menú anterior", "description": "Volver a preguntas frecuentes"},
                {"id": "inicio",     "title": "🏠 Inicio",        "description": "Ir al menú principal"},
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

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "info-catastro-4"})
    return [payload]
