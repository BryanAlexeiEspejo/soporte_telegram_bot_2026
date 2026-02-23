# app/services/handlers/atm/A_3_4_pregunta_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"
def _short(t, n=MAX_DESC): t=(t or "").strip(); return t if len(t)<=n else t[:n-1]+ELLIPSIS
def _row(i, ti, d): return {"id": i, "title": ti, "description": _short(d)}

# ✅ Respuesta 3-4
async def manejar_A_3_4_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Puedo pagar por internet?*\n"
        "R. ¡Sí! Puedes pagar desde la *banca por internet* de los siguientes bancos:\n\n"
        "🏦 Banco BISA S.A. — https://www.bisa.com\n"
        "🏦 Banco Nacional de Bolivia — https://www.bnb.com.bo\n"
        "🏦 Banco Económico S.A. — https://www.baneco.com.bo\n"
        "🏦 Banco de Crédito BCP — https://www.bcp.com.bo\n"
        "🏦 Banco Unión S.A. — https://www.bancounion.com.bo\n"
        "🏦 Banco Ganadero S.A. — https://www.bg.com.bo\n"
        "🏦 Banco FIE S.A. — https://www.bancofie.com.bo\n"
        "🏦 Banco Fortaleza — https://www.bancofortaleza.com.bo\n"
        "🏦 Banco Mercantil Santa Cruz — https://www.bmsc.com.bo\n"
        "🏦 Banco PRODEM — https://www.prodem.bo\n"
        "🏦 Banco Sol — https://www.bancosol.com.bo\n"
        "🏦 Coop. Jesús Nazareno — https://www.jesus-nazareno.coop\n"
        "🏦 Coop. San Martín de Porres — https://www.cosmart.coop\n\n"
        "Si un enlace no abre, cópialo y pégalo en tu navegador.\n"
        "\n*Actualizado:*\nOctubre 15 por Yesid Flores Huayhua (ATM)\n"
        "\n*Selecciona una pregunta:*"
    )

    q1 = "¿Cómo debo proceder para acogerme al beneficio?"
    q2 = "¿Cómo puedo pagar mi deuda tributaria con la Ley de Condonación?"
    q3 = "¿Dónde puedo pagar mis impuestos de forma personal?"
    q4 = "¿Puedo pagar por internet?"
    q5 = "¿Qué necesito para realizar el pago?"
    q6 = "¿Puedo imprimir mi comprobante de pago?"
    #q7 = "¿Dónde puedo consultar mi deuda para acceder al beneficio del perdonazo?"
    q8 = "¿Qué necesito para acceder a las facilidades de pago?"

    secciones = [
        {
        "title": "Preguntas",
        "rows": [
            _row("q-atm-3-1", "Procedimiento", "📝 Pasos para acceder al beneficio."),
            _row("q-atm-3-2", "¿Cómo pagar?", "💳 Formas de pago disponibles con la Ley 573."),
            _row("q-atm-3-3", "Pago personal", "🏛️ Dónde pagar presencialmente tus tributos."),
            _row("q-atm-3-4", "Pago por Internet", "🌐 Opciones para pagar en línea."),
            _row("q-atm-3-5", "Requisitos", "📄 Qué documentos o datos necesitas."),
            _row("q-atm-3-6", "Imprimir pago", "🖨️ Cómo obtener tu comprobante impreso."),
            #_row("q-atm-3-7", "Consultar deuda", "🔎 Dónde ver tu deuda antes de pagar."),
            _row("q-atm-3-8", "Facilidades de pago", "💰 Requisitos para acceder a cuotas."),
        ],
    },
        {"title": "Navegación", "rows": [
            {"id": "atm-3",  "title": "⬅️ Menú anterior", "description": _short("Volver a Formas y lugares de pago")},
            {"id": "inicio", "title": "🏠 Inicio",         "description": _short("Ir al menú principal")},
        ]},
    ]

    payload = await crear_payload_lista(numero=numero, cuerpo=cuerpo, opciones=secciones,
                                        header_text="", footer_text="", button_text="Opciones disponibles")
    return [payload]
