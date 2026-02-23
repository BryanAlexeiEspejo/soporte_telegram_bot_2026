# app/services/handlers/atm/A_1_4_pregunta_1.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

def _row(row_id: str, title: str, desc: str) -> Dict:
    return {"id": row_id, "title": title, "description": desc}

# ✅ Respuesta 1-4
async def manejar_A_1_4_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Hasta cuándo tengo plazo para acogerme al beneficio?*\n"
        "R. Puedes acogerte hasta el 30 de abril de 2026.\n"
        "\n*Actualizado:*\nOctubre 15 por Yesid Flores Huayhua (ATM)\n"
        "\n*Selecciona una pregunta:*"
    )

    q1 = "¿Qué es la Ley Municipal Autonómica N° 573 de Alivio Tributario?"
    q2 = "¿Quiénes pueden beneficiarse con esta Ley?"
    q3 = "¿Desde cuándo está en vigencia esta Ley?"
   

    secciones = [
        {
            "title": "Preguntas",
            "rows": [
                _row("q-atm-1-1", "¿Qué es?", q1),
                _row("q-atm-1-2", "¿Quiénes?", q2),
                _row("q-atm-1-3", "Sobre su vigencia", q3),
           
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "atm-1",    "title": "⬅️ Menú anterior", "description": "Volver a preguntas"},
                {"id": "atm-menu", "title": "🏛️ Menú anterior", "description": "Volver a Administración Tributaria Municipal – ATM"},
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
        button_text="Ver preguntas",
    )
    return [payload]
