# app/services/handlers/catastro/D_3_12_info_catastro_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_3_12_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Es obligatorio usar el Formulario Único de Solicitud (FUS) para todos los trámites en el archivo de catastro?*\n"
        "R.- Sí, es obligatorio, ya que es donde se genera y especifica el requerimiento de la documentación solicitada.\n"
        "------------------------------\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-3-p2", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 9–12"},
            {"id": "inicio",             "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero, cuerpo=cuerpo, opciones=secciones,
        header_text="", footer_text="", button_text="Opciones disponibles"
    )
    return [payload]
