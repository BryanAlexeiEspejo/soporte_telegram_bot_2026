# app/services/handlers/catastro/C_puntos_horarios_atencion.py

from typing import List, Dict, Optional
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

# =========================
# Utilidades (límites WABA)
# =========================
_WA_LIMITS = {
    "row_title": 24,
    "row_desc": 72,
    "section_title": 24,
    "button_text": 20,
    "header_text": 60,
    "footer_text": 60,
    "body_text": 1024,  # del mensaje interactivo (no el de texto plano)
}

def _truncate(s: str, n: int) -> str:
    if s is None:
        return ""
    return s if len(s) <= n else s[: max(0, n - 1)] + "…"

def _sanitize_sections(secciones: List[Dict]) -> List[Dict]:
    sane = []
    for sec in secciones:
        sec_title = _truncate(sec.get("title", ""), _WA_LIMITS["section_title"])
        rows_in = sec.get("rows", []) or []
        rows_out = []
        for r in rows_in:
            rows_out.append({
                "id": r["id"],  # no tocamos el ID para no romper tus handlers
                "title": _truncate(r.get("title", ""), _WA_LIMITS["row_title"]),
                "description": _truncate(r.get("description", ""), _WA_LIMITS["row_desc"]),
            })
        sane.append({"title": sec_title, "rows": rows_out})
    return sane

def _safe_button_text(txt: str) -> str:
    return _truncate(txt or "Ver opciones", _WA_LIMITS["button_text"])

def _safe_text(txt: str, max_len_key: str) -> str:
    return _truncate(txt or "", _WA_LIMITS[max_len_key])

# ------------------------------
# MENÚ "SERVICIOS CATASTRALES"
# ------------------------------
async def enviar_menu_catastro_principal(numero: str, name: Optional[str] = None) -> Dict:
    # saludo seguro (sin variable no definida)
    _ = f"👋 ¡Hola! " if name else "👋 ¡Hola! "
    cuerpo = (
        "👋 ¡Hola! te encuentras en la sección de información catastral.\n"
        "Aquí podrás consultar los requisitos de trámites, horarios de atención, direcciones y más.\n"
        "👉 Selecciona una de las opciones disponibles en información catastral para continuar:"
    )

    secciones = [
        {
            "title": "📚 Servicios catastrales",
            "rows": [
                {"id": "catastro-a", "title": "Consulta trámite",
                 "description": "👉 Revisa el estado de tu trámite catastral."},
                # {"id": "catastro-b", "title": "Requisitos catastro",
                #  "description": "📄 Documentos para iniciar o completar tu trámite."},
                # {"id": "catastro-c", "title": "Puntos y horarios",
                #  "description": "🕓 Oficinas, direcciones y horarios de atención."},
                # {"id": "catastro-e", "title": "Contactos y dir.",
                #  "description": "📍 Teléfonos y direcciones de contacto."},
                # {"id": "inicio", "title": "Volver al inicio",
                #  "description": "Regresar al menú principal."},
            ],
        }
    ]

    secciones = _sanitize_sections(secciones)

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=_safe_text(cuerpo, "body_text"),
        opciones=secciones,
        header_text="",   # Al pasar vacío, tu helper debería omitir header
        footer_text="",
        button_text=_safe_button_text("Ver opciones"),
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "menu-principal"})
    return payload


# ------------------------------
# MENÚ: Trámites + Navegación
# ------------------------------
def obtener_opciones_catastro() -> list:
    seccion_principal = {
        "title": "Trámites disponibles",
        "rows": [
            {"id": "req-catastro-1", "title": "Certificado registro", "description": "Trámite por primera vez"},
            {"id": "req-catastro-2", "title": "Duplicado certificado", "description": "Reposición por extravío"},
            {"id": "req-catastro-3", "title": "Actualización registro", "description": "Cambio de datos catastrales"},
            {"id": "req-catastro-4", "title": "Copias legalizadas", "description": "Documentos oficiales"},
            {"id": "req-catastro-5", "title": "Certif. Ley 247", "description": "Ley de regularización"},
            {"id": "req-catastro-6", "title": "Reclamos y denuncias", "description": "Reportar irregularidades"},
        ],
    }

    seccion_navegacion = {
        "title": "Navegación",
        "rows": [
            {"id": "volver-menu-catastro", "title": "⬅️ Volver", "description": "Volver a información catastral"},
            {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al inicio"},
        ],
    }
    return [seccion_principal, seccion_navegacion]


# ---------------------------------------
# HANDLER: Puntos y horarios de atención
# ---------------------------------------
async def manejar_puntos_horarios(numero: str) -> List[Dict]:
    # 1) Mensaje de texto (largo) con direcciones/links
    cuerpo_largo = (
        "Puntos y horarios de atención:\n\n"
        "☑ Consulta inicial e información:\n"
        "Oficinas Potosí y Colón, Edificio Tobia (plataforma de atención ciudadana).\n"
        "Cómo llegar: https://maps.app.goo.gl/afTLfYVm5pUhCNSQ8\n\n"
        "PIAC SUR (Edificio “Atlanta”, Av. Ballivián entre calles 13 y 14, zona Calacoto).\n"
        "Cómo llegar: https://maps.app.goo.gl/513ba6Yy9iuslfVo9\n\n"
        "☑ Ingresar y recoger trámites (plataformas integrales):\n\n"
        "CAMACHO\n"
        "Dirección: Av. Camacho, Centro Comercial Camacho Nivel 1.\n"
        "Horario: 8:45 a 16:15 (continuo).\n"
        "Cómo llegar: https://maps.app.goo.gl/XQRE17M7SnFHT596\n\n"
        "SUR\n"
        "Dirección: Av. Gral. José Ballivián Nº720, entre calles 13 y 14, Edif. ATLANTA (PB), Calacoto.\n"
        "Horario: 8:45 a 16:15 (continuo).\n"
        "Cómo llegar: https://maps.app.goo.gl/513ba6Yy9iuslfVo9\n\n"
        "MIRAFLORES\n"
        "Dirección: Calle Chichas esq. Juan de Vargas, Edif. ESPRA PB, Z. Miraflores.\n"
        "Horario: 8:45 a 16:15 (continuo).\n"
        "Cómo llegar: https://maps.app.goo.gl/DqS8UsMUqbxmixjR9\n"
        "────────────────────────"
    )

    payload_texto = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"preview_url": True, "body": cuerpo_largo},
    }

    # 2) Lista interactiva con límites corregidos (títulos ≤ 24)
    secciones = [
        {
             "title": "Trámites disponibles",
        "rows": [
            {"title": "Certificado registro", "id": "req-catastro-1", "description": "Trámite por primera vez"},
            {"title": "Duplicado certificado", "id": "req-catastro-2", "description": "Reposición por extravío"},
            {"title": "Actualización registro", "id": "req-catastro-3", "description": "Cambio de datos catastrales"},
            {"title": "Copias legalizadas", "id": "req-catastro-4", "description": "Documentos oficiales"},
            {"title": "Certif. Ley 247", "id": "req-catastro-5", "description": "Ley de regularización"},
            {"title": "Reclamos y denuncias", "id": "req-catastro-6", "description": "Reportar irregularidades"},
        ],
        },
        {
             "title": "Navegación",  
        
        "rows": [
            {"id": "catastro-b", "title": "⬅️ Volver", "description": "Volver a información catastral"},
            {"id": "inicio", "title": "🏠 Inicio", "description": "Volver al inicio"},
        ],
        },
    ]

    secciones = _sanitize_sections(secciones)

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=_safe_text("👉 Selecciona una opción para continuar:", "body_text"),
        opciones=secciones,
        header_text="",   # vacío => el helper debería omitir header
        footer_text="",
        button_text=_safe_button_text("Opciones disponibles"),
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "puntos-horarios-menu"})
    return [payload_texto, payload_lista]