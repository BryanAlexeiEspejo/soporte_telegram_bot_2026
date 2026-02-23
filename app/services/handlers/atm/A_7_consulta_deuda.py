from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista


def _row(row_id: str, title: str, desc: str) -> Dict:
    return {"id": row_id, "title": title, "description": desc}


# ✅ Consulta tu deuda – Ley 573
async def manejar_consulta_deuda(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Dónde puedo consultar mi deuda para acceder al beneficio del perdonazo?*\n"
        "R. Puedes consultar si tienes deudas pendientes y acogerte a los beneficios "
        "de la Ley N° 573 de Alivio Tributario en los siguientes enlaces oficiales:\n\n"
        "🏠 *Inmuebles:*\n"
        "https://n9.cl/8f6y1\n\n"
        "🚗 *Vehículos:*\n"
        "https://n9.cl/xg2hc\n\n"
        "💼 *Patentes Municipales:*\n"
        "https://n9.cl/8w616\n\n"
        "\n*Fuente actualizada hasta:*\nOct. 15 por Yesid Flores Huayhua (ATM)\n\n"
        "*Selecciona una opción:*"
    )

    secciones = [
        {
            "title": "Navegación",
            "rows": [
                {"id": "atm-menu", "title": "🏛️ ATM", "description": "Volver a Administración Tributaria Municipal"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Ir al menú principal"},
            ],
        }
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="Consulta tu deuda",
        footer_text="",
        button_text="Opciones disponibles",
    )
    return [payload]
