from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# Carácter invisible para ocultar el “title” en las filas de preguntas
INVISIBLE = "\u2063"  # fallback: "\u200B"

def _row_info(row_id: str, texto: str) -> Dict:
    return {"id": row_id, "title": INVISIBLE, "description": texto}

# ✅ Respuesta 5-1
async def manejar_A_5_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
       
        "*¿Qué pasa si no me acojo a la Ley?*\n"
        "R. Si no te acoges antes del 30 de abril de 2026, los procesos de cobro que estaban suspendidos se reactivarán y perderás el beneficio de condonación.\n"
        "\n*Actualizado:*\nOctubre 15 por Yesid Flores Huayhua (ATM)\n"
     
        "\n*Selecciona una pregunta:*"
    )

    # Pregunta única (16)
    q16 = "¿Qué pasa si no me acojo a la Ley?"

    secciones = [
        {
            "title": "Preguntas",
            "rows": [
                _row_info("q-atm-5-1", q16),
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "atm-5",    "title": "⬅️ Menú anterior", "description": "Volver a preguntas"},
                {"id": "atm-menu", "title": "🏛️ ATM",           "description": "Volver a Administración Tributaria Municipal"},
                {"id": "inicio",   "title": "🏠 Inicio",         "description": "Ir al menú principal"},
            ],
        },
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Opciones disponibles",
    )
    return [payload]
