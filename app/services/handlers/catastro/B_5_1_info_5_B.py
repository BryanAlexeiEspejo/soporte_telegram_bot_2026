from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_info_emision_cert_ley247_b(numero: str) -> List[Dict]:
    dataList = []

    # ✅ Texto explicativo completo
    cuerpo = (
        "*¿Dónde se realiza el trámite?*\n\n"
        "✅ *Orientación sobre los requisitos y pasos a seguir:*\n"
        "En oficinas de la *calle Potosí y Colón*, edificio Tobia, plataforma de atención ciudadana.\n"
        "*Horario:* 8:45 hrs. a 16:15 hrs. (horario continuo).\n"
        "*Cómo llegar:* https://maps.app.goo.gl/aiTLfYVm5pUhCN5Q8\n\n"
        "✅ *Ingresar y recoger trámites:*\n"
        "En cualquiera de las siguientes plataformas integrales:\n\n"
        "*CAMACHO*\n"
        "• Dirección: Av. Camacho, Centro Comercial Camacho Nivel 1.\n"
        "• Horario: 8:45 hrs. a 16:15 hrs. (continuo).\n"
        "• Cómo llegar: https://maps.app.goo.gl/XQtRE17M7SnFHT596\n\n"
        "*SUR*\n"
        "• Dirección: Av. Gral. José Ballivián N°720, entre calles 13 y 14 Calacoto, Planta Baja, Edif. ATLANTA.\n"
        "• Horario: 8:45 hrs. a 16:15 hrs. (continuo).\n"
        "• Cómo llegar: https://maps.app.goo.gl/513ba6Yy9iusifVo9\n\n"
        "*MIRAFLORES*\n"
        "• Dirección: Calle Chichas esq. Juan de Vargas, Edificio ESPRA PB, Z. Miraflores.\n"
        "• Horario: 8:45 hrs. a 16:15 hrs. (continuo).\n"
        "• Cómo llegar: https://maps.app.goo.gl/DqS8UsMUqbxmixjR9"
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

    # ✅ Payload tipo lista
    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📘 Emisión de Certificado (Ley 247)",
        footer_text="",
        button_text="Opciones disponibles"
    )
    dataList.append(payload_lista)

    # ✅ Estado actualizado
    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "emision-cert-ley247-info-b"
    })

    return dataList
