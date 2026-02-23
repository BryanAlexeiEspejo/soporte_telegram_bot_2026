# app/services/handlers/atm/A_2_Alcance_beneficios_alivio.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"

def _short(text: str, n: int = MAX_DESC) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1] + ELLIPSIS

def _row(row_id: str, title: str, description: str) -> Dict:
    return {"id": row_id, "title": title, "description": _short(description)}

# ✅ Enviar 1) TEXTO EXACTO (sin cambiar nada) + 2) LISTA de navegación
async def manejar_alcance_beneficios_alivio(numero: str) -> List[Dict]:
    # 1) TEXTO — contenido EXACTO tal como lo proporcionaste
    cuerpo_texto = (
        "*Beneficios*\n"
       
        "*¿Qué impuestos están incluidos en esta Ley de condonación?*\n"
        "   R. Los siguientes impuestos municipales:\n"
        "• Impuesto Municipal a la Propiedad de Bienes Inmuebles (IMPBI)\n"
        "• Impuesto Municipal a la Propiedad de Vehículos Automotores Terrestres (IMPVAT)\n"
        "• Impuesto Municipal a las Transferencias (IMT)\n"
        "• Impuesto Municipal a las Transferencias Onerosas (IMTO)\n"
        "• Patentes Municipales (PM)\n\n"
        "*¿Desde qué año hasta qué año se condonarán intereses, multas y sanciones con esta Ley?*\n"
        "•\tDesde la gestión 2012 hasta la 2023 para Inmuebles, Vehículos .\n"
        "•\tDesde la gestión 1995 hasta 2023 para Transferencias Onerosas (IMT, IMTO).\n"
        "•\tDesde la gestión 2016 hasta la 2023 para Patentes Municipales\n\n"
        "*¿Qué beneficios obtengo si me acojo a esta Ley?*\n"
        "   R. Al acogerte a la Ley N° 573, solo pagarás el monto total del tributo omitido, actualizando la fecha de pago, sin intereses, sin multas ni sanciones.\n\n"
        "*¿Qué pasa si ya pagué mi deuda antes de esta Ley?*\n"
        "   R. Si ya realizaste el pago total de tus tributos antes de la vigencia de la Ley N° 573, no necesitas acogerte al beneficio, ya que tu deuda se encuentra regularizada y no tienes obligaciones pendientes con el Gobierno Autónomo Municipal de La Paz. La Ley de Alivio Tributario está dirigida únicamente a quienes aún tienen deudas por pagar."
        "\n\n*Fuente actualizada hasta:*\nOct. 15 por Yesid Flores Huayhua (ATM)\n"
    )

    payload_texto = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {"body": cuerpo_texto, "preview_url": False},
    }

    # 2) LISTA — navegación breve
    cuerpo_nav = "\u200B"
    secciones = [
        {
            "title": "Navegación",
            "rows": [
                _row("atm-menu", "🏛️ Menú anterior", "Volver a Administración Tributaria Municipal – ATM"),
                _row("inicio",   "🏠 Inicio",         "Ir al menú principal"),
            ],
        },
    ]

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo_nav,
        opciones=secciones,
        header_text="",       # strings vacíos para header/footer
        footer_text="",
        button_text="Ver opciones",
    )

    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-2"})
    return [payload_texto, payload_lista]
