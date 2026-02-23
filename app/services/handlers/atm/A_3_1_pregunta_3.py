# app/services/handlers/atm/A_3_1_pregunta_3.py
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

async def manejar_A_3_1_respuesta(numero: str) -> List[Dict]:
    # 1) TEXTO — título en negrita y sangría corta en la respuesta
    cuerpo_texto = (
        "*De forma personal*\n"
        " Paga en entidades financieras autorizadas:\n"
        " • Banco BISA S.A.\n"
        " • Banco de Crédito BCP\n"
        " • Banco Económico S.A.\n"
        " • Banco FIE S.A.\n"
        " • Banco Fortaleza\n"
        " • Banco Ganadero S.A.\n"
        " • Banco Mercantil Santa Cruz S.A.\n"
        " • Banco Nacional de Bolivia S.A.\n"
        " • Banco PRODEM S.A.\n"
        " • Banco Sol\n"
        " • Banco Unión S.A.\n"
        " • Banco PyME de la Comunidad S.A.\n"
        " • Banco PyME Ecofuturo S.A.\n"
        " • CIDRE IFD\n"
        " • COOP. San Martín de Porres\n"
        " • CRECER IFD\n"
        " • DIACONÍA IFD\n"
        " • IDEPRO IFD\n"
        " • La Primera E.F.V.\n"
        " • Cajas en oficinas de la Administración Tributaria Municipal del "
        "Gobierno Autónomo Municipal de La Paz (calle Mercado y Colón, Ex Banco del Estado)\n\n"
        "Luego de realizar tu pago, puedes imprimir tu comprobante desde el sitio web del RUAT "
        "o desde la banca por internet del banco que utilizaste.\n"
        "\n*Fuente actualizada hasta:*\nOct. 15 por Yesid Flores Huayhua (ATM)\n"
    )

    payload_texto = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {"body": cuerpo_texto, "preview_url": False},
    }

    # 2) LISTA — dos opciones + navegación (body < 1024)
    cuerpo_lista = "*¿Dónde pagar?*\nSelecciona una opción:"
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
                
                _row("atm-3",  "⬅️ Menú anterior", "Volver a Formas y lugares de pago"),
                _row("atm-menu", "🏛️ Menú anterior", "Volver a Administración Tributaria Municipal – ATM"),
                _row("inicio", "🏠 Inicio",         "Ir al menú principal"),
            ],
        },
    ]

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo_lista,
        opciones=secciones,
        header_text="",     # strings vacíos para evitar errores en validadores
        footer_text="",
        button_text="Ver opciones",
    )

    # Mantener contexto/estado para navegación
    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-3-1"})
    return [payload_texto, payload_lista]
