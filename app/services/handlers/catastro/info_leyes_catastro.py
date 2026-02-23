from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista, crear_payload_texto
from app.database.database import set_estado_usuario

async def manejar_info_leyes(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    # ✅ PRIMER MENSAJE: texto con todas las leyes
    cuerpo_largo = (
        "📘 *Normativa y leyes municipales de Catastro*\n\n"
        "• Ley de Catastro:\n"
        "https://catastro.lapaz.bo/download/ley-de-catastro/\n\n"
        "• Decreto Municipal Nº 15/2014:\n"
        "https://catastro.lapaz.bo/download/decreto-municipal-no-15-2014/\n\n"
        "• Resolución Ejecutiva Nº 342/2012:\n"
        "https://catastro.lapaz.bo/download/resolucion-ejecutiva-no-342-2012/\n\n"
        "• Directrices de Catastro:\n"
        "https://catastro.lapaz.bo/download/directrices-de-catastro/\n\n"
        "• Ordenanza Municipal Nº 472/2016:\n"
        "https://catastro.lapaz.bo/download/ordenanza-municipal-no-472-2016-registro-catastral-en-el-marco-de-la-ley-247/\n\n"
        "• Resolución Ejecutiva Nº 316/2021:\n"
        "https://catastro.lapaz.bo/download/resolucion-ejecutiva-no-316-2021-aprobacion-de-fichas-catastrales/\n\n"
        "• Resolución Administrativa Nº 201/2021:\n"
        "https://catastro.lapaz.bo/download/resolucion-administrativa-no-201-2021-modificacion-del-formato-del-certificado-catastral/\n\n"
        "• Ordenanza Municipal Nº 193/2010:\n"
        "https://catastro.lapaz.bo/download/ordenanza-municipal-no-193-2010-solicitud-de-certificado-de-registro-catastral-sobrepuesta-con-propiedad-municipal/\n\n"
        "• Ordenanza Municipal Nº 456/2009:\n"
        "https://catastro.lapaz.bo/download/ordenanza-municipal-n-456-2009-reglamento-de-gestion-de-aires-de-rio/\n\n"
        "• Resolución Municipal de Márgenes de Tolerancia:\n"
        "https://catastro.lapaz.bo/download/resolucion-municipal-de-margenes-de-tolerancia/"
    )

    # ✅ Primer mensaje: cuerpo largo en texto
    payload_texto = await crear_payload_texto(
        numero=numero,
        cuerpo=cuerpo_largo
    )
    dataList.append(payload_texto)

    # ✅ SEGUNDO MENSAJE: menú tipo LIST
    cuerpo_menu = "Selecciona una opción"

    secciones = [
        {
            "title": "Navegación",
            "rows": [
                {
                    "id": "catastro-b",
                    "title": "⬅️ Volver",
                    "description": "Ver requisitos de trámites catastrales"
                },
                {
                    "id": "inicio",
                    "title": "🏠 Inicio",
                    "description": "Volver al inicio"
                },
            ],
        }
    ]

    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo_menu,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Opciones disponibles",
    )
    dataList.append(payload_menu)

    # ✅ Actualizamos el estado del usuario
    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "leyes-catastro"})

    return dataList
