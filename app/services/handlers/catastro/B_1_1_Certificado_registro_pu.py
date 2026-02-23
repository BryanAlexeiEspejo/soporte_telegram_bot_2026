from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

# (Dejo tu constante y helper original sin usarlos, por si los necesitas en otros menús)
INVISIBLE = "\u2063"   # Invisible Separator

def _row(row_id: str, title: str, description: str) -> Dict:
    """Fila con título corto y descripción completa (la pregunta)."""
    return {"id": row_id, "title": title, "description": description}

async def manejar_certificado_pu(numero: str) -> List[Dict]:
    dataList: List[Dict] = []

    # ⚠️ NO TOCAR: cuerpo queda exactamente igual
    cuerpo = (
        "*📄 Requisitos certificado de registro catastral en Propiedad Unifamiliar (PU) — vivienda o terreno.*\n\n"
        "*Requisitos:*\n"
        "• Testimonio de propiedad (original y fotocopia).\n"
        "• Folio real o tarjeta de propiedad (original y fotocopia).\n"
        "• Testimonio del anterior propietario o certificado trienal/origen (original y fotocopia), "
        "solo si no existe folio real o no se puede relacionar con antecedentes dominiales.\n"
        "• Cédula de identidad del/los propietarios (original y fotocopia).\n"
        "• Boleta de pago de impuestos (fotocopia).\n"
        "• Ficha catastral “A” en dos ejemplares (emitida por profesional externo).\n"
        "• Fotografías de la fachada, interiores y exteriores, con referencias "
        "(emitidas por profesional externo).\n\n"
        "*📚 Recursos y documentación:*\n"
        "Descargar fichas catastrales A, B, C.\n"
        "Normativa y leyes municipales catastrales.\n"
    )

    secciones = [
        {
            "title": "Información útil",
            "rows": [
                _row("info-a", "Sin testimonio", "¿Qué pasa si no tiene el testimonio de propiedad (original y fotocopia)?"),
                _row("info-b", "¿Dónde?", "¿Dónde se realiza este trámite?"),
                _row("info-c", "Definición", "¿Qué es un certificado de registro catastral?"),
                _row("info-d", "Finalidad", "¿Para qué sirve el certificado de registro catastral?"),
                _row("info-e", "Costo", "¿Tiene un costo?"),
                _row("info-f", "Resultado", "¿Qué obtengo al hacer este trámite?"),
                _row("info-g", "Quiénes", "¿Quién puede realizar este trámite?"),
            ],
        },
        {
            "title": "Recursos adicionales",
            "rows": [
                {"id": "info-fichas", "title": "📥 Fichas A, B, C", "description": "Descargar fichas catastrales A, B, C."},
                {"id": "info-leyes", "title": "📘 Normativa catastral", "description": "Normativa y leyes municipales de catastro."},
            ],
        },
        {
            "title": "Navegación",  # sin icono, como pediste
            "rows": [
                {"id": "catastro-b", "title": "⬅️ Volver atrás", "description": "Regresar al menú anterior"}
            ],
        },
    ]

    payload_menu = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",                 # encabezado opcional
        footer_text="",                 # pie opcional
        button_text="Información útil", # texto del botón del LIST
    )

    dataList.append(payload_menu)

    await set_estado_usuario(
        numero,
        {"contexto": "catastro", "estado": "certificado-pu-preguntas"}
    )

    return dataList
