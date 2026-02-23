
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"
def _short(t, n=MAX_DESC): t=(t or "").strip(); return t if len(t)<=n else t[:n-1]+ELLIPSIS
def _row(i, ti, d): return {"id": i, "title": ti, "description": _short(d)}

# ✅ Respuesta 6-3
async def manejar_A_6_3_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*¿Qué pasa si realizo la Modificación de Datos Técnicos posteriores a la Ley Nº 573?*\n"
        "R. Pierde los beneficios de la condonación de Multas, Intereses y Sanciones.\n"
        "\n*Actualizado:*\nOctubre 15 por Yesid Flores Huayhua (ATM)\n"
        "\n*Selecciona una pregunta:*"
    )

    q1 = "¿Puedo beneficiarme de la Ley Nº 573 si tengo procesos de fiscalización?"
    q2 = "¿Si me dejan una invitación puedo acogerme a la Ley Nº 573?"
    q3 = "¿Qué pasa si realizo la Modificación de Datos Técnicos posteriores a la Ley Nº 573?"
    q4 = "¿Si pago mis impuestos atrasados al contado tengo descuento?"

    secciones = [
        {
        "title": "Preguntas",
        "rows": [
            _row("q-atm-6-1", "Fiscalización", "⚖️ ¿Puedes acoger el perdonazo si tienes problemas de fiscalización?"),
            _row("q-atm-6-2", "Invitación", "📨 ¿Si te dejaron invitación aún puedes acceder?"),
            _row("q-atm-6-3", "Datos modificados", "📝 ¿Qué pasa si cambias datos después?"),
            _row("q-atm-6-4", "Pago al contado", "💵 ¿Si pagas tus impuestos atrasados al contado hay descuento?"),
        ],
        },
        {"title": "Navegación", "rows": [
            {"id": "atm-6",  "title": "⬅️ Menú anterior", "description": _short("Volver a Atención y soporte")},
            {"id": "atm-menu", "title": "🏛️ ATM",           "description": "Volver a Administración Tributaria Municipal"},
            {"id": "inicio", "title": "🏠 Inicio",         "description": _short("Ir al menú principal")},
        ]},
    ]

    payload = await crear_payload_lista(
        numero=numero, cuerpo=cuerpo, opciones=secciones,
        header_text="", footer_text="", button_text="Opciones disponibles"
    )
    return [payload]
