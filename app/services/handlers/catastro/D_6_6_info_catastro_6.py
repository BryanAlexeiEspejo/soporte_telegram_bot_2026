# app/services/handlers/catastro/D_6_6_info_catastro_6.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_6_6_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué alternativas tengo si necesito un documento catastral que no se encuentra en el archivo de la calle Potosí?*\n"
        "R.- Toda la documentación respecto a antecedentes catastrales se encuentra en el Archivo del Edificio Tobia.\n"
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
