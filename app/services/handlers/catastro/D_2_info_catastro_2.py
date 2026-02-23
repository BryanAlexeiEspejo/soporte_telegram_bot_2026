# app/services/handlers/catastro/D_2_info_catastro_2.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

# ✅ LIST con secciones (Preguntas + Navegación), cumpliendo límites de WhatsApp
async def manejar_info_catastro_2(numero: str) -> List[Dict]:
    # Mostrar las preguntas "tal cual" en el cuerpo
    cuerpo = (
        "🏛️ *Infraestructura y atención al ciudadano*\n\n"
        "1. ¿Dónde se encuentra el área de archivo de catastro y cuál es su horario de atención?\n"
        "2. ¿Puedo obtener copias legalizadas en alguna otra plataforma que no sea la de la calle Potosí?\n\n"
        "Selecciona una opción:"
    )

    q1 = "¿Dónde se encuentra el área de archivo de catastro y cuál es su horario de atención?"
    q2 = "¿Puedo obtener copias legalizadas en alguna otra plataforma que no sea la de la calle Potosí?"

    secciones = [
        {
            "title": "Preguntas (1–2)",
            "rows": [
                {"id": "q-catastro-2-1", "title": "1", "description": _short(q1)},
                {"id": "q-catastro-2-2", "title": "2", "description": _short(q2)},
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-d", "title": "⬅️ Menú anterior", "description": "Volver a preguntas"},
                {"id": "inicio",         "title": "🏠 Inicio",        "description": "Ir al menú principal"},
            ],
        },
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,   # tu helper debe mapear a "interactive.sections"
        header_text="",
        footer_text="",
        button_text="Ver preguntas"    # ≤20
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "info-catastro-2"})
    return [payload]
