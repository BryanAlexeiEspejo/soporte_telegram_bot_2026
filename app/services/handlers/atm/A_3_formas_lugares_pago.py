# app/services/handlers/atm/A_3_formas_lugares_pago.py
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

# ✅ 3. Formas y lugares de pago
async def manejar_formas_lugares_pago(numero: str) -> List[Dict]:
    # 1) MENSAJE TEXTO (con fuente al final como “footer visual”)
    cuerpo_texto = (
        "*FORMAS Y LUGARES DE PAGO*\n"
        "Dónde, cómo y hasta cuándo pagar tu deuda.\n\n"

        "*¿Qué necesito para realizar el pago?*\n"
        "  R. Solo necesitas:\n"
        " • El número de Registro Tributario del inmueble o la placa/póliza del vehículo.\n"
        " • Una cuenta activa en un banco autorizado o acceso a banca por internet.\n"
        " • El importe a pagar. Puedes consultarlo en:\n"
        "   • Portal Tributario del RUAT (inmueble o vehículo).\n"
        "   • Aplicación Tu Municipio 24/7 (inmueble o vehículo).\n"
        "   • Portal Tributario de la ATM (Patentes Municipales).\n\n"

        "*¿Cómo debo proceder para acogerme al beneficio?*\n"
        "  R. Acércate a las oficinas de la Administración Tributaria Municipal (ATM) o a los puntos de atención habilitados y solicita la proforma de pago con el detalle de tu deuda.\n"
        " También puedes ir directamente a las cajas recaudadoras de entidades financieras autorizadas con el número de placa (vehículos) o con el número de inmueble registrado en el Padrón Municipal de Contribuyentes.\n\n"

        "*¿Cómo puedo pagar mi deuda tributaria con la Ley de Condonación?*\n"
        "  R. Existen dos alternativas:\n"
        " • *Pago al contado:* cancelando el total de tu deuda.\n"
        " • *Facilidades de pago:*\n"
        "  • Desde el 9 de diciembre hasta la vigencia de la Ley, 30% de pago inicial y el saldo hasta en 12 meses.\n\n"

        "*¿Qué necesito para acceder a las facilidades de pago?*\n"
        "  R. Presenta en plataformas de atención de la ATM los documentos según corresponda:\n"
        " • *Personas naturales:* CI vigente (original y fotocopia).\n"
        " • *Herederos:* documento legal de herencia (original y fotocopia) y CI del heredero.\n"
        " • *Personas jurídicas:* testimonio de poder del representante legal (si no está registrado) y su CI.\n"
        " • *Apoderados:* poder notariado para trámites tributarios y CI del apoderado.\n"
        " • *Poseedores de buena fe (vehículos):* CI y uno de los siguientes: minuta de compra-venta, CRPVA o documentación de importación.\n"
        " • *Formulario de solicitud:* se genera en plataforma al iniciar el trámite (N° 499 Inmuebles, N° 500 Vehículos, N° 501 Patentes).\n"
        " • *Pago inicial:* debe realizarse el mismo día que se genera el formulario.\n\n"

        "Luego de realizar tu pago, puedes imprimir tu comprobante desde el sitio web del RUAT o desde la banca por internet del banco utilizado.\n\n"
        "*Consultar deuda:*\n"
        "- Puede consultar su deuda ingresando al sistema ruat:  www.ruat.gob.bo donde podrás obtener tu proforma.\n"
        "- Escríbenos al whatsapp: 62443034 – 71552352\n\n"
        "*Fuente actualizada hasta:*\nEne. 14 por Yesid Flores Huayhua (ATM)"
    )

    payload_texto = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {"body": cuerpo_texto, "preview_url": False},
    }

    # 2) MENÚ LISTA (SIN footer)
    cuerpo_lista = "\u200B"
    secciones = [
        {
            "title": "¿Dónde pagar?",
            "rows": [
                _row("q-atm-3-1", "De forma personal", "Paga en entidades financieras autorizadas."),
                _row("q-atm-3-2", "Pagar por internet", "Paga desde la banca por internet."),
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                _row("atm-menu", "🏛️ Menú anterior", "Volver a Administración Tributaria Municipal – ATM"),
                _row("inicio", "🏠 Inicio", "Ir al menú principal"),
            ],
        },
    ]

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo_lista,
        opciones=secciones,
        header_text="",
        footer_text="",  # ← vacío para evitar error WA
        button_text="¿Dónde pagar?",
    )

    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-3"})
    return [payload_texto, payload_lista]
