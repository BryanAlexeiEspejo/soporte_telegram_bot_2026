from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_emision_cert_ley247_f(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Cuerpo del mensaje
    cuerpo = (
        "*¿Qué obtengo al hacer este trámite?*\n\n"
        "Al finalizar el proceso, el ciudadano obtiene un Certificado de Registro Catastral, con la superficie real de su terreno.\n\n"

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

    # ✅ Crear el payload de lista
    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Emisión Certificado Ley 247",
        footer_text="",
        button_text="Opciones disponibles"
    )
    dataList.append(payload_lista)

    # ✅ Guardar el estado del usuario
    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "emision-cert-ley247-info-e"
    })

    return dataList
