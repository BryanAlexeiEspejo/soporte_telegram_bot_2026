# app/services/handlers/catastro/D_3_6_info_catastro_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_3_6_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Cómo puedo solicitar un certificado de no existencia catastral?*\n"
        "R.- El G.A.M.L.P. no emite certificaciones de inexistencia catastral.\n"
        "------------------------------\n"
    )
    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-3", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–8"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ],
    }]
    payload = await crear_payload_lista(numero=numero, cuerpo=cuerpo, opciones=secciones,
                                        header_text="", footer_text="", button_text="Opciones disponibles")
    return [payload]
