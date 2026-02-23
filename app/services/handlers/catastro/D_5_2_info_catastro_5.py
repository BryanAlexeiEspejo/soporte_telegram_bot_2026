# app/services/handlers/catastro/D_5_2_info_catastro_5.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_5_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Puedo realizar el trámite en nombre de una tercera persona?*\n"
        "R.- Si, adjuntando el documento de poder notarial otorgado por el propietario en el que autoriza al apoderado recabar información.\n"
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
