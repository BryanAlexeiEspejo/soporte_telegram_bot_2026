# app/services/handlers/atm/A_3_2_pregunta_3.py
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

# ✅ Respuesta: ¿Dónde pagar? — Pagar por internet (misma info, con más separación visual)
# Enviamos 1) TEXTO con el detalle y 2) LISTA corta para navegar
async def manejar_A_3_2_respuesta(numero: str) -> List[Dict]:
    cuerpo_texto = (
        "*Pagar por internet*\n"
        " Puedes pagar desde la banca por internet.\n\n"

        " *Bancos habilitados (sitio web):*\n"
        " • Banco BISA S.A. — www.bisa.com\n\n"
        " • Banco Nacional de Bolivia — www.bnb.com.bo\n\n"
        " • Banco Económico S.A. — www.baneco.com.bo\n\n"
        " • Banco de Crédito BCP — www.bcp.com.bo\n\n"
        " • Banco Unión S.A. — www.bancounion.com.bo\n\n"
        " • Banco Ganadero S.A. — www.bg.com.bo\n\n"
        " • Banco FIE S.A. — www.bancofie.com.bo\n\n"
        " • Banco Fortaleza — www.bancofortaleza.com.bo\n\n"
        " • Banco Mercantil Santa Cruz — www.bmsc.com.bo\n\n"
        " • Banco PRODEM — www.prodem.bo\n\n"
        " • Banco Sol — www.bancosol.com.bo\n\n"
        " • Coop. Jesús Nazareno — www.jesus-nazareno.coop\n\n"
        " • Coop. San Martín de Porres — www.cosmart.coop\n\n"

        "Luego de realizar tu pago, puedes imprimir tu comprobante desde el sitio web del RUAT "
        "o desde la banca por internet del banco que utilizaste.\n"
        "\n*Fuente actualizada hasta:*\nOct. 15 por Yesid Flores Huayhua (ATM)\n"
    )

    payload_texto = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {"body": cuerpo_texto, "preview_url": False},  # evitar previews de enlaces
    }

    # LISTA (dos opciones + navegación). Body < 1024.
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
                _row("atm-3",   "⬅️ Menú anterior", "Volver a Formas y lugares de pago"),
                _row("atm-menu","🏛️ Menú anterior", "Volver a Administración Tributaria Municipal – ATM"),
                _row("inicio",  "🏠 Inicio",         "Ir al menú principal"),
            ],
        },
    ]

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo_lista,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Ver opciones",
    )

    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-3-2"})
    return [payload_texto, payload_lista]
