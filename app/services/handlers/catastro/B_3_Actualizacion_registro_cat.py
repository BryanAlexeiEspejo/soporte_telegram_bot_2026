from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_actualizacion_registro(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    # ⚠️ NO TOCAR: el cuerpo queda exactamente igual
    cuerpo = (
        "*Requisitos para actualización del registro catastral a solicitud directa.*\n"
        "• Certificado de registro catastral: vigente (posterior a octubre de 2012).\n"
        "• Cédula de identidad: Copia simple de la cédula de identidad del propietario o apoderado.\n"
        "• Testimonio de propiedad: Copia del documento que acredita la propiedad del inmueble.\n"
        "• Folio Real actualizado: Informe de Derechos Reales que demuestre la situación legal actual del predio.\n"
        "• Boleta de pago de impuestos (fotocopia).\n"
        
        "*Importante:*\n"
        "Debes acudir a la plataforma de atención ciudadana en la calle Potosí, en horarios de 8:45 a 15:30 hrs., "
        "y solicitar el servicio de \"Actualización\" toda la documentación deberá estar ordenada en un folder con fastener "
        "(sólo fotocopias).\n"
        "*Las actualizaciones se dan en los siguientes casos:*\n"
        "• Cuando el registro anterior pierde vigencia.\n"
        "• Por modificaciones físicas del predio.\n"
        "• Por modificaciones legales.\n"
        # "✅ Recursos y documentación:\n"
        # "1. Descargar fichas catastrales A, B, C.\n"
        # "2. Normativa y leyes municipales catastro."
    )

    header = ""
    footer = ""

    secciones = [
        {
            "title": "Información útil",
            "rows": [
                {"id": "ar-info-b", "title": "¿Dónde?", "description": "¿Dónde se realiza este trámite?"},
                {"id": "ar-info-c", "title": "Definición", "description": "¿Que es una actualización de registro catastral?"},
                {"id": "ar-info-d", "title": "Finalidad", "description": "¿Para que sirve un certificado de registro catastral?"},
                {"id": "ar-info-e", "title": "Costo", "description": "¿Tiene un costo?"},
                {"id": "ar-info-f", "title": "Resultado", "description": "¿Qué obtengo con este trámite?"},
                {"id": "ar-info-g", "title": "Quiénes", "description": "¿Quién puede realizar este trámite?"},
            ],
        },
        {
            "title": "Recursos adicionales",
            "rows": [
                {"id": "info-fichas", "title": "📥 Fichas A, B, C", "description": "Descargar fichas catastrales A,B,C."},
                {"id": "info-leyes", "title": "📘 Normativa catastral", "description": "Normativa y leyes municipales catastro."}
            ]
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-b", "title": "⬅️ Volver", "description": "Regresar al menú anterior"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Menú principal de AMI"}
            ]
        }
    ]

    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text=header,
        footer_text=footer,
        button_text="Información útil"
    )

    dataList.append(payload_menu)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "actualizacion-registro-preguntas"
    })

    return dataList
