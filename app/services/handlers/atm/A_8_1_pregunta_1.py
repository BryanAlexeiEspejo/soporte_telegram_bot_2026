# app/services/handlers/atm/A_8_1_pregunta_1.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
ELLIPSIS = "…"

def _short(t, n=MAX_DESC):
    t = (t or "").strip()
    return t if len(t) <= n else t[:n-1] + ELLIPSIS

def _row(i, ti, d):
    return {"id": i, "title": ti, "description": _short(d)}

# ✅ Respuesta detallada a q-atm-8-1
async def manejar_A_8_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "*Facilidad de Pago (Plan de Pagos)*\n"
        "Desde el 9 de diciembre de 2025 hasta la vigencia de la Ley pagando el 30% de pago inicial y el saldo hasta en 12 meses.\n\n"
        "*¿Qué necesito para acceder a las facilidades de pago?*\n\n"
        "R. Presenta en la plataforma de Facilidades de Pago de la ATM los documentos según corresponda:\n\n"
        "• Personas naturales: CI vigente (original y fotocopia).\n"
        "• Herederos: documento legal de herencia (original y fotocopia) y CI del heredero.\n"
        "• Personas jurídicas: testimonio de poder del representante legal (si no está registrado) y su CI.\n"
        "• Apoderados: poder notariado para trámites tributarios y CI del apoderado.\n"
        "• Poseedores de buena fe (vehículos): CI y uno de: minuta de compra-venta, CRPVA o documentación de importación.\n"
        "• Formulario de solicitud: se genera en plataforma al iniciar el trámite (N° 499 Inmuebles, N° 500 Vehículos, N° 501 Patentes).\n"
        "• Pago inicial: debe realizarse el mismo día que se genera el formulario.\n\n"
        "*Fuente actualizada:*\n"
        "Dic. 2 por Yesid Flores Huayhua (ATM)\n\n"
      
    )

    secciones = [
        {
            "title": "Navegación",
            "rows": [
    
                {"id": "atm-menu", "title": "🏛️ ATM",                     "description": _short("Volver a Administración Tributaria Municipal")},
                {"id": "inicio",   "title": "🏠 Inicio",                   "description": _short("Ir al menú principal")},
            ],
        },
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Opciones"
    )

    return [payload]
