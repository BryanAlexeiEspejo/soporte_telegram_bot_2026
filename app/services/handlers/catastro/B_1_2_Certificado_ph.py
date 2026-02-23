from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_certificado_ph(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    # ⚠️ NO TOCAR: cuerpo queda exactamente igual
    cuerpo = (
        "*📄 Certificado de Registro Catastral en propiedad horizontal (PH) para un departamento*\n\n"
        "*Requisitos:*\n"
        "• Testimonio de propiedad (original y fotocopia).\n"
        "• Folio real o tarjeta de propiedad (original y fotocopia).\n"
        "• Testimonio del anterior propietario o certificado trienal o de origen "
        "(original y fotocopia) – si no hay folio real o antecedentes dominiales.\n"
        "• CI del/de los propietarios (original y fotocopia).\n"
        "• Boleta de pago de impuestos (fotocopia).\n"
        "• Plano funcional aprobado (original y fotocopia).\n"
        "• Ficha Catastral “C” (2 ejemplares, profesional externo).\n"
        "• Tabla de fraccionamiento aprobada – si no existe matriz habilitada.\n"
        "• Ficha Catastral “B” (2 ejemplares) – si no existe matriz habilitada.\n"
        "• Aprobaciones anteriores (legalizadas) si son previas a 2003.\n\n"
        "*📚 Recursos:*\n"
        "Descargar fichas A, B, C.\n"
        "Normativa catastral vigente.\n\n"
    )

    secciones = [
        {
            "title": "Información útil",
            "rows": [
                {"id": "info-a", "title": "Sin testimonio", "description": "¿Que pasa si no tiene el testimonio de propiedad (original y fotocopia)?"},
                {"id": "info-b", "title": "¿Dónde?", "description": "¿Dónde se realiza el trámite?"},
                {"id": "info-c", "title": "Definición", "description": "¿Qué es un certificado de registro catastral?"},
                {"id": "info-d", "title": "Finalidad", "description": "¿Para que sirve el certificado de registro catastral?"},
                {"id": "info-e", "title": "Costo", "description": "¿Tiene un costo?"},
                {"id": "info-f", "title": "Resultado", "description": "¿Qué obtengo al hacer este trámite?"},
                {"id": "info-g", "title": "Quiénes", "description": "¿Quién puede realizar este trámite?"},
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
                {"id": "catastro-b", "title": "⬅️ Volver", "description": "Regresar al menú anterior"}
                # {"id": "inicio", "title": "🏠 Inicio", "description": "Menú principal de AMI"}
            ]
        }
    ]

    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Información util"
    )

    dataList.append(payload_menu)

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "certificado-ph-preguntas"
    })

    return dataList
