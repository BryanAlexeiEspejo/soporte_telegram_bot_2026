# app/services/handlers/catastro/D_1_info_catastro_1_respuesta_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_3_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué es una ficha/formulario/etc. catastral?*\n"
        "R.- Ficha Catastral: Instrumento técnico que sirve para el "
        "relevamiento, en sitio, de la información territorial, que puede "
        "tomar diferentes nombres, como ser Formulario 100-5, CIM 02, "
        "Formulario Único de Registro Catastral u otros. No constituye "
        "parte indisoluble del Certificado de Registro Catastral.\n"
        "------------------------------\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            {
                "id": "info-catastro-1",
                "title": "⬅️ Menú anterior",
                "description": "Volver a preguntas"
            },
            {
                "id": "inicio",
                "title": "🏠 Inicio",
                "description": "Ir al menú principal"
            }
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,                 # Texto principal (≤1024)
        opciones=secciones,            # 1 sección con 2 filas
        header_text="",                # no tocar
        footer_text="",                # no tocar
        button_text="Opciones disponibles"  # <= 20
    )

    return [payload]
