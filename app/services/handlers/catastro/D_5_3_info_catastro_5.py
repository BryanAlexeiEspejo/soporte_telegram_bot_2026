# app/services/handlers/catastro/D_5_3_info_catastro_5.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_5_3_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Puedo solicitar información o copias de documentos si soy un heredero del propietario original?*\n"
        "R.- A la presentación del testimonio de declaratoria de herederos.\n"
        "------------------------------\n"
    )
    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-5", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–6"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ],
    }]
    payload = await crear_payload_lista(numero=numero, cuerpo=cuerpo, opciones=secciones,
                                        header_text="", footer_text="", button_text="Opciones disponibles")
    return [payload]
