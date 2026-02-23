from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_emision_cert_ley247_c(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Cuerpo explicativo
    cuerpo = (
        "*¿Qué es una emisión de certificado de registro catastral a través del Servicio Municipal de Catastro en el marco de la Ley 247?*\n\n"
        "Consiste en el levantamiento de la información de las características físicas de un bien inmueble "
        "(superficie de terreno, superficie construida y otros), el registro de la información en el Módulo de Catastro "
        "del Sistema de Información Territorial (SIT) del Gobierno Autónomo Municipal de La Paz y finalmente la emisión del "
        "Certificado Catastral el cual determina la ubicación geográfica, características físicas y la valoración del bien inmueble."
    )

   # ✅ Función auxiliar para crear filas
    def _row(id_: str, title: str, description: str) -> Dict:
        return {"id": id_, "title": title, "description": description}

    # ✅ Menú de navegación y preguntas
    secciones = [
        {
            "title": "Información útil",
            "rows": [
                _row("rec-info-b", "¿Dónde se realiza?", "¿Dónde se realiza este trámite?"),
                _row("rec-info-c", "Definición", "¿Qué es una emisión de certificado de registro catastral (Ley 247)?"),
                _row("rec-info-d", "Finalidad", "¿Para qué sirve un certificado de registro catastral?"),
                _row("rec-info-e", "Costo", "¿Tiene costo este trámite?"),
                _row("rec-info-f", "Resultado", "¿Qué obtengo al hacer el trámite?"),
                _row("rec-info-g", "Quiénes pueden", "¿Quién puede realizar este trámite?"),
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-b", "title": "⬅️ Volver", "description": "Regresar al menú anterior"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Menú principal de AMI"},
            ],
        },
    ]

    # ✅ Crear lista tipo WhatsApp
    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Emisión Certificado Ley 247",
        footer_text="",
        button_text="Opciones disponibles"
    )
    dataList.append(payload_lista)

    # ✅ Guardar estado actual del usuario
    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "emision-cert-ley247-info-c"
    })

    return dataList
