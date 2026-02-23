# app/services/handlers/catastro/D_7_1_info_catastro_7.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Respuesta 7-1
async def manejar_info_catastro_7_1_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Se necesita permiso para hacer un cuarto fuera de mi casa?*\n"
        "R.- Corresponde apersonarse a la plataforma de atención al ciudadano ubicado en edificio ex soboce planta baja para que recabe información y requisitos por la DDAT.\n"
        "------------------------------\n"
    )

    secciones = [{
        "title": "Navegación",
        "rows": [
            {"id": "info-catastro-7", "title": "⬅️ Menú anterior", "description": "Volver a preguntas 1–2"},
            {"id": "inicio",          "title": "🏠 Inicio",        "description": "Ir al menú principal"},
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero, cuerpo=cuerpo, opciones=secciones,
        header_text="", footer_text="", button_text="Opciones disponibles"
    )
    return [payload]
