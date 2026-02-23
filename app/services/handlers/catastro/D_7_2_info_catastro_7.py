# app/services/handlers/catastro/D_7_2_info_catastro_7.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista

# ✅ Respuesta 7-2
async def manejar_info_catastro_7_2_respuesta(numero: str) -> List[Dict]:
    cuerpo = (
        "------------------------------\n"
        "*¿Qué documentos necesito para solicitar copias simples o legalizadas en el archivo de catastro?*\n"
        "R.- Necesita presentar: Fotocopia simple del carnet de identidad, fotocopia simple del folio, fotocopia simple del pago de impuestos, fotocopia simple de poder (en caso de ser apoderado). Presentados por el titular o apoderado.\n"
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
