# app/services/handlers/catastro/D_5_5_info_catastro_5.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_5_5_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Puede un copropietario solicitar información o copias de documentos sin la presencia de los otros copropietarios?*\n"
        "R.- Sí puede, en tanto su nombre figure en el folio, demostrando así su derecho propietario.\n"
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
