# app/services/handlers/catastro/D_3_9_info_catastro_3.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

async def manejar_info_catastro_3_9_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué tipos de documentos puedo solicitar en copia simple o legalizada en el archivo de catastro?*\n"
        "R.- Puede solicitar en fotocopia simple: Certificado de Registro Catastral, Ficha Catastral, "
        "Reporte de Datos Generales, Mosaico Catastral, Informes Técnicos de Observaciones.\n"
        "Las copias que puede solicitar en legalizadas: Ficha Catastral, Reporte de Datos Generales, "
        "Mosaico Catastral, Informes Técnicos de Observaciones.\n"
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
