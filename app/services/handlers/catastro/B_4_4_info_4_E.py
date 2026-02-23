from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_copias_legalizadas_e(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Cuerpo explicativo del costo del trámite
    cuerpo = (
        "*¿Tiene un costo este trámite?*\n\n"
        "El costo varía dependiendo del documento y la cantidad de copias solicitadas. "
        "Se consulta directamente en las plataformas de atención ciudadana o en las oficinas pertinentes.\n\n"
        "*Pago de la Tasa:*\n"
        "• Realiza el pago correspondiente por la copia legalizada, que es de 18,90 Bs.\n"
        "• Si es una Fotocopia Legalizada de Levantamiento Topográfico del Servicio Municipal de Catastro:\n"
        "   ◦ Ingresa una nota solicitando la copia legalizada por medio de SITRAM.\n"
        "   ◦ Verifica que hayas pagado el levantamiento topográfico del Servicio Municipal de Catastro.\n"
        "   ◦ Una vez confirmado el pago, podrás pagar los 18,90 Bs. por la copia legalizada."
    )

    secciones = [
        {
            "title": "Información útil",
            "rows": [
                {"id": "rcl-info-b", "title": "Dónde se realiza", "description": "¿Dónde se realiza el trámite?"},
                {"id": "rcl-info-c", "title": "Qué es", "description": "¿Qué es una copia legalizada?"},
                {"id": "rcl-info-d", "title": "Para qué sirve", "description": "¿Para qué sirve un certificado de registro catastral?"},
                {"id": "rcl-info-e", "title": "Costo", "description": "¿Tiene un costo este trámite?"},
                {"id": "rcl-info-f", "title": "Resultado", "description": "¿Qué obtengo al hacer este trámite?"},
                {"id": "rcl-info-g", "title": "Quién puede realizarlo", "description": "¿Quién puede realizar este trámite?"}
            ]
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "rcl", "title": "⬅️ Volver", "description": "Volver al menú anterior"},
                {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al inicio"}
            ]
        }
    ]

    # ✅ Crear lista interactiva
    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Copias Legalizadas",
        footer_text="",
        button_text="Opciones disponibles"
    )
    dataList.append(payload_lista)

    # ✅ Guardar estado
    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "copias-legalizadas-info-e"
    })

    return dataList
