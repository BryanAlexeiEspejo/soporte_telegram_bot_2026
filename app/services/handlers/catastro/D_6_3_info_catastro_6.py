# app/services/handlers/catastro/D_6_3_info_catastro_6.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_6_3_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cómo puedo cambiar el uso de suelo de mi propiedad?*\n"
        "R.- A través de la dirección de desarrollo y administración territorial previa solicitud de requisitos en la plataforma a de atención al ciudadano ubicado en el edificio ex soboce planta baja.\n"
        "------------------------------\n"
    )
    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-6", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–7"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ],
    }]
    payload = await crear_payload_lista(numero=numero, cuerpo=cuerpo, opciones=secciones,
                                        header_text="", footer_text="", button_text="Opciones disponibles")
    return [payload]
