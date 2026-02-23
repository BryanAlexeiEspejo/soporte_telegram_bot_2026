from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_certificado_registro(numero: str) -> List[Dict]:
    dataList = []

    cuerpo = (
        "*📄 Certificado de registro catastral*\n\n"
        "Existen dos tipos de certificación catastral según tu necesidad:\n"
        "• Propiedad Unifamiliar (PU): para una vivienda o terreno.\n"
        "• Propiedad Horizontal (PH): para un departamento.\n\n"
        "👉 Selecciona el tipo de certificado que deseas solicitar:"
    )

    header = ""      # si tu helper incluye header cuando es "", cámbialo a None en el helper
    footer = ""

    seccion_principal = {
        "title": "Selecciona una opción",
        "rows": [
            {
                "id": "certificado-pu",
                "title": "1️⃣ Unifamiliar (PU)",
                # ≤72 chars
                "description": "Certificado catastral en Prop. Unifamiliar (PU): vivienda o terreno."
            },
            {
                "id": "certificado-ph",
                "title": "2️⃣ Horizontal (PH)",
                # ≤72 chars
                "description": "Certificado catastral en Prop. Horizontal (PH): depto/condominio."
            }
        ]
    }

    seccion_navegacion = {
        "title": "Navegación",
        "rows": [
            {
                "id": "catastro-b",
                "title": "⬅️ Volver atrás",
                "description": "Volver a ver los trámites catastrales."
            },
            {
                "id": "inicio",
                "title": "🏠 Inicio",
                "description": "Volver al Inicio"
            }
        ]
    }

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=[seccion_principal, seccion_navegacion],
        header_text=header,
        footer_text=footer,
        button_text="Ver certificados"   # ≤20 chars, OK
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "certificado-opcion"})

    dataList.append(payload)
    return dataList
