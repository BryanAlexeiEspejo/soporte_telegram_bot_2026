# app/services/handlers/catastro/D_1_info_catastro_1_respuesta_10.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Un solo mensaje (LIST) con la respuesta + opciones de navegación
async def manejar_info_catastro_10_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cuál es la importancia de tener un Certificado de Registro Catastral?*\n"
        "R.- La certificación catastral constituye el acto y es el único documento "
        "oficial mediante el cual el Gobierno Autónomo Municipal de La Paz brinda "
        "seguridad jurídica a los administrados y da constancia del registro de un "
        "bien inmueble en el Catastro, consignando los datos físicos, económicos "
        "y/o jurídicos inscritos.\n"
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
        button_text="Opciones disponibles"  # ≤20
    )

    return [payload]
