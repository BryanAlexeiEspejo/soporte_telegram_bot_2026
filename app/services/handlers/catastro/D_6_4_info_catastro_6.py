# app/services/handlers/catastro/D_6_4_info_catastro_6.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_6_4_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Dónde se encuentra el área de archivo de catastro y cuál es su horario de atención?*\n"
        "R.- Se encuentra ubicado en el edificio Tobía planta baja, su atención a través de la plataforma de atención al ciudadano de lunes a viernes en los horarios de 08:45 a 16:15 (continuo).\n"
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
