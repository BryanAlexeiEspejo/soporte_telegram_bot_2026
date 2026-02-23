# app/services/handlers/atm/A_6_atencion_y_soporte.py
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

# ✅ 6. Preguntas frecuentes — envía 1) el texto exacto y 2) un menú de navegación
async def manejar_atencion_y_soporte(numero: str) -> List[Dict]:
    # 1) MENSAJE — texto EXACTO tal como lo solicitaste (sin cambios)
    body_text = (
        "Preguntas frecuentes\n"
        "*¿Qué es la Ley Municipal Autonómica N° 573 de Alivio Tributario?*\n"
        "   R. Es una ley aprobada por el Gobierno Autónomo Municipal de La Paz que establece un periodo voluntario de regularización y condonación tributaria. Permite a los contribuyentes ponerse al día con sus impuestos sin pagar intereses, multas ni sanciones, hasta el 30 de abril de 2026.\n\n"
        "*¿Quiénes pueden beneficiarse con esta Ley?*\n"
        "   R. Todos los sujetos pasivos, terceros responsables y poseedores de buena fe (solo vehículos) que tengan deudas pendientes en los impuestos municipales dentro de la jurisdicción del Municipio de La Paz.\n\n"
        "*¿Desde cuándo y hasta qué fecha está en vigencia esta Ley Nº 573?*\n"
        "   R. Entra en vigencia desde el 23 de octubre de 2025.hasta el 30 de abril de 2026.\n\n"
        "*¿Puedo beneficiarme de la Ley Nº 573 si tengo procesos de fiscalización?*\n"
        "   R.- Puedes beneficiarte siempre y cuando se actualice primero la información que se observa en el proceso y luego puede realizar el pago al contado o mediante facilidades de pago.\n\n"
        "*¿Si me dejan una invitación puedo acogerme a la Ley Nº 573?*\n"
        "   R.- Si, previamente actualiza la información o Datos Técnicos observados puede beneficiarse con esta Ley.\n\n"
        "*¿Qué pasa si realizo la Modificación de Datos Técnicos posteriores a la Ley Nº 573 ?*\n"
        "   R.- Pierde los beneficios de la condonación de Multas, Intereses y Sanciones.\n\n"
        "*¿Si pago mis impuestos atrasados al contado tengo descuento?*\n"
        "   R.- No, la Ley Nº 573 solamente condona Multas, Interés y Sanciones."
    )

    payload_texto = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {"body": body_text, "preview_url": False},
    }

    # 2) MENÚ — navegación breve
    cuerpo_nav = "\u200B"
    secciones = [
        {
            "title": "Navegación",
            "rows": [
                _row("atm-menu", "🏛️ Menú anterior", "Volver a Administración Tributaria Municipal – ATM"),
                _row("inicio",   "🏠 Inicio",         "Ir al menú principal"),
            ],
        }
    ]
    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo_nav,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Ver opciones",
    )

    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-6"})
    return [payload_texto, payload_lista]
