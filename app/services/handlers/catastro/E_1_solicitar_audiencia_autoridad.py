from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_texto, crear_payload_lista

async def manejar_solicitud_audiencia_acm(numero: str) -> List[Dict]:
    dataList = []

    # 🟩 Mensaje principal
    texto = (
        "*📅 Solicitar audiencia con la Autoridad Catastral Municipal (ACM):*\n\n"
        "✅ Las audiencias deben ser programadas. El jefe de catastro, *Ing. Carlos Jose Medrano Rodríguez*, le atenderá previa audiencia programada.\n\n"
        "📝 Puede solicitarla mediante correspondencia ciudadana, con una *nota simple* ingresada por ventanilla de SITRAM (calle Potosí, edificio Tobia, planta baja).\n"
        "🕘 De lunes a viernes, de 8:45 am a 16:10 pm.\n\n"
        "📥 *Descargar nota modelo:* http://35.232.232.3:4002/NOTA_DE_SOLICITUD_DE_AUDIENCIA.docx"
    )
    payload_texto = await crear_payload_texto(numero, texto)
    dataList.append(payload_texto)

    # 🟩 Menú de opciones tipo lista
    seccion_menu = {
        "title": "📑 Más información",
        "rows": [
            {
                "id": "descargar-nota",
                "title": "📥 Descargar nota",
                "description": "Modelo de nota oficial",
            },
            {
                "id": "entregar-nota",
                "title": "📬 Dónde entregarla",
                "description": "Horario y ubicación para entrega",
            },
            {
                "id": "atras",
                "title": "🔙 Volver atrás",
                "description": "Regresar al menú anterior",
            }
        ]
    }

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo="¿Qué deseas saber sobre la audiencia?",
        opciones=[seccion_menu],
        footer_text="Municipio de La Paz",
        header_text="Selecciona una opción",
        button_text="Ver opciones"
    )
    dataList.append(payload_lista)

    # 🟩 Guardamos estado para submenú
    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "audiencia-acm"})
    return dataList
