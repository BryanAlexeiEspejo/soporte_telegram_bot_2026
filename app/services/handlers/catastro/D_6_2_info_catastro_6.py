# app/services/handlers/catastro/D_6_2_info_catastro_6.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_6_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué pasa si no registro mi inmueble en el catastro?*\n"
        "R.- Todo propietario de bien inmueble que  se encuentre dentro del municipio de la paz está obligado a registrar y actualizar la información sobre cambios técnicos y/o legales producidos respecto al mismo ante el G.A.M.L.P.\n"
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
