# app/services/telegram_templates.py
from typing import Dict, List, Any, Optional, Tuple
from app.services.telegram_service import telegram_service, safe_html

# -------------------------
# CONFIG / UTILS INTERNOS
# -------------------------
DEFAULT_PARSE_MODE = "HTML"


def _wrap_payload(
    chat_id: int,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: Optional[str] = DEFAULT_PARSE_MODE,
    **extra
) -> Dict[str, Any]:
    payload = {
        "chat_id": chat_id,
        "text": safe_html(text),
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    payload.update(extra)
    return payload


def _chunk_list(items: List[Any], page: int, page_size: int) -> Tuple[List[Any], int]:
    """Devuelve items de la página y total páginas (1-indexed)."""
    if page_size <= 0:
        page_size = 10
    total = max(1, (len(items) + page_size - 1) // page_size)
    page = max(1, min(page, total))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total


# -------------------------
# PLANTILLAS PRINCIPALES
# -------------------------
class TelegramTemplates:
    """Colección amplia de plantillas reutilizables para Telegram."""

    # ---- Menús ----
    @staticmethod
    async def main_menu(chat_id: int, name: str, show_not_understood: bool = False) -> Dict[str, Any]:
        name_safe = safe_html(name)
        extra = "Creo que no te entendí bien 🤔, vamos a intentarlo otra vez.\n\n" if show_not_understood else ""
        text = (
            f"👋 <b>¡Hola {name_safe}!</b>\n\n"
            f"{extra}"
            f"Soy <b>AMI</b>, tu asistente municipal inteligente.\n\n"
            f"<b>Selecciona una opción:</b>"
        )
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "🔐 Recuperar contraseña IGOB", "callback_data": "igob"}],
            [{"text": "🏛️ Administración Tributaria", "callback_data": "atm"}],
            [{"text": "📄 Seguimiento de trámites", "callback_data": "tramites"}],
            [{"text": "🗺️ Información catastral", "callback_data": "catastro"}],
            [{"text": "👤 Información ciudadana", "callback_data": "ciudadano"}],
            [{"text": "⭐ Calificar", "callback_data": "calificar"}],
        ])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def help_menu(chat_id: int) -> Dict[str, Any]:
        text = (
            "<b>Ayuda - Comandos disponibles</b>\n\n"
            "/start - Iniciar conversación\n"
            "/menu - Mostrar menú principal\n"
            "/tramites - Ver estado de trámites\n"
            "/contacto - Contactar soporte\n\n"
            "También puedes escribir libremente tu consulta."
        )
        return _wrap_payload(chat_id, text)

    # ---- Mensajes comunes ----
    @staticmethod
    async def welcome_message(chat_id: int, name: str) -> Dict[str, Any]:
        name_safe = safe_html(name)
        text = (
            f"👋 <b>¡Hola {name_safe}!</b>\n\n"
            "Bienvenido a <b>AMI</b>, tu Agente Municipal Inteligente.\n\n"
            "Escribe 'hola' o usa el menú para comenzar."
        )
        return _wrap_payload(chat_id, text)

    @staticmethod
    async def loading(chat_id: int, text: str = "Procesando, por favor espera...") -> Dict[str, Any]:
        return _wrap_payload(chat_id, f"⏳ {text}")

    @staticmethod
    async def success(chat_id: int, text: str) -> Dict[str, Any]:
        return _wrap_payload(chat_id, f"✅ {text}")

    @staticmethod
    async def error(chat_id: int, text: str = "Ocurrió un error. Intenta nuevamente.") -> Dict[str, Any]:
        return _wrap_payload(chat_id, f"❌ {text}")

    @staticmethod
    async def unknown_command(chat_id: int) -> Dict[str, Any]:
        text = "🤔 No entendí eso. Puedes escribir 'ayuda' para ver las opciones o usar /menu."
        return _wrap_payload(chat_id, text)

    # ---- Confirmaciones y decisiones ----
    @staticmethod
    async def yes_no_prompt(chat_id: int, text: str, yes_payload: str = "yes", no_payload: str = "no") -> Dict[str, Any]:
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "✅ Sí", "callback_data": yes_payload}, {"text": "❌ No", "callback_data": no_payload}]
        ])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def confirm_delete(chat_id: int, item_name: str, confirm_payload: str, cancel_payload: str = "cancel") -> Dict[str, Any]:
        text = f"⚠️ ¿Deseas eliminar <b>{safe_html(item_name)}</b>? Esta acción no se puede deshacer."
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "Eliminar ❌", "callback_data": confirm_payload}],
            [{"text": "Cancelar ✅", "callback_data": cancel_payload}]
        ])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    # ---- Formularios / entrada guiada ----
    @staticmethod
    async def ask_for_contact(chat_id: int, text: str = "Por favor comparte tu contacto:") -> Dict[str, Any]:
        keyboard = telegram_service.create_reply_keyboard([["Compartir contacto"]])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def ask_for_location(chat_id: int, text: str = "Por favor comparte tu ubicación:") -> Dict[str, Any]:
        keyboard = telegram_service.create_reply_keyboard([["Enviar ubicación"]])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def form_field_prompt(chat_id: int, field_label: str, example: Optional[str] = None) -> Dict[str, Any]:
        ex = f" (ej: {example})" if example else ""
        text = f"✍️ Ingresa {field_label}{ex}:"
        return _wrap_payload(chat_id, text)

    # ---- Listados y paginación ----
    @staticmethod
    async def paginated_list(
        chat_id: int,
        title: str,
        items: List[str],
        page: int = 1,
        page_size: int = 6,
        callback_prefix: str = "item"
    ) -> Dict[str, Any]:
        page_items, total_pages = _chunk_list(items, page, page_size)
        lines = "\n".join([f"• {safe_html(it)}" for it in page_items]) or "— No hay resultados —"
        text = f"<b>{safe_html(title)}</b>\n\n{lines}\n\nPágina {page}/{total_pages}"

        # construir keyboard con cada item como callback e instrucciones de paginado
        buttons = []
        for idx, it in enumerate(page_items, start=1 + (page - 1) * page_size):
            buttons.append([{"text": it[:30], "callback_data": f"{callback_prefix}:{idx}"}])

        # paginación (prev / siguiente)
        nav_row = []
        if page > 1:
            nav_row.append({"text": "⬅️ Anterior", "callback_data": f"{callback_prefix}:page:{page-1}"})
        if page < total_pages:
            nav_row.append({"text": "Siguiente ➡️", "callback_data": f"{callback_prefix}:page:{page+1}"})
        if nav_row:
            buttons.append(nav_row)

        keyboard = telegram_service.create_inline_keyboard(buttons)
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    # ---- Templates específicos del dominio (ATM, Catastro, Tramites, IGOB, Ciudadano) ----
    @staticmethod
    async def atm_options(chat_id: int) -> Dict[str, Any]:
        text = "<b>ATM - Opciones disponibles</b>\n\nSelecciona lo que necesitas:"
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "🧾 Estado de deudas", "callback_data": "atm:deudas"}],
            [{"text": "💳 Pagos y formas", "callback_data": "atm:pagos"}],
            [{"text": "📄 Requisitos", "callback_data": "atm:requisitos"}],
            [{"text": "⬅️ Volver", "callback_data": "menu"}],
        ])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def igob_recovery_init(chat_id: int) -> Dict[str, Any]:
        text = (
            "<b>Recuperación de contraseña IGOB</b>\n\n"
            "Para comenzar, ingresa tu número de cédula o el correo registrado."
        )
        return _wrap_payload(chat_id, text)

    @staticmethod
    async def tramites_summary(chat_id: int, tramites: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        tramites: lista de dicts con keys: id, tipo, estado, fecha
        """
        if not tramites:
            return _wrap_payload(chat_id, "No encontramos trámites asociados a tu número.")

        lines = []
        for t in tramites[:10]:
            lines.append(f"• <b>{safe_html(t.get('tipo','Trámite'))}</b> — {safe_html(t.get('estado','Desconocido'))} ({safe_html(t.get('fecha','-'))})")
        text = "<b>Resultados - Trámites</b>\n\n" + "\n".join(lines)
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "Ver todos los trámites", "callback_data": "tramites:ver_todos"}],
            [{"text": "Volver al menú", "callback_data": "menu"}]
        ])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def catastro_info(chat_id: int, parcel_id: str, summary: str) -> Dict[str, Any]:
        text = (
            f"<b>Información catastral — {safe_html(parcel_id)}</b>\n\n"
            f"{safe_html(summary)}"
        )
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "Ver planos", "callback_data": f"catastro:planos:{parcel_id}"}],
            [{"text": "Solicitar certificado catastral", "callback_data": f"catastro:cert:{parcel_id}"}],
            [{"text": "Volver", "callback_data": "menu"}],
        ])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def ciudadano_info(chat_id: int, info_text: str) -> Dict[str, Any]:
        text = f"<b>Información ciudadana</b>\n\n{safe_html(info_text)}"
        return _wrap_payload(chat_id, text)

    # ---- Multimedia / docs (devuelven payload que puedes usar con sendMessage o sendPhoto/sendDocument helpers) ----
    @staticmethod
    async def photo_message(chat_id: int, photo_url: str, caption: str = "") -> Dict[str, Any]:
        # Nota: este payload es pensado para pasarlo a telegram_service.send_photo
        return {
            "chat_id": chat_id,
            "photo_url": photo_url,
            "caption": safe_html(caption),
            "parse_mode": DEFAULT_PARSE_MODE
        }

    @staticmethod
    async def document_message(chat_id: int, document_url: str, caption: str = "") -> Dict[str, Any]:
        return {"chat_id": chat_id, "document_url": document_url, "caption": safe_html(caption)}

    # ---- Admin / broadcast helpers ----
    @staticmethod
    async def admin_broadcast_preview(chat_id: int, text: str, confirm_payload: str = "broadcast:confirm") -> Dict[str, Any]:
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "Confirmar envío a todos ✅", "callback_data": confirm_payload}],
            [{"text": "Cancelar ❌", "callback_data": "broadcast:cancel"}],
        ])
        return _wrap_payload(chat_id, f"⚠️ Vista previa del broadcast:\n\n{safe_html(text)}", reply_markup=keyboard)

    # ---- Feedback / rating ----
    @staticmethod
    async def feedback_prompt(chat_id: int) -> Dict[str, Any]:
        keyboard = telegram_service.create_inline_keyboard([
            [{"text": "⭐ Excelente", "callback_data": "feedback:5"}],
            [{"text": "🙂 Bueno", "callback_data": "feedback:4"}],
            [{"text": "😐 Regular", "callback_data": "feedback:3"}],
            [{"text": "😕 Malo", "callback_data": "feedback:2"}],
            [{"text": "😡 Pésimo", "callback_data": "feedback:1"}],
        ])
        return _wrap_payload(chat_id, "¿Cómo calificarías la atención?", reply_markup=keyboard)

    # ---- Utilidades rápidas ----
    @staticmethod
    async def back_button(chat_id: int, text: str = "Volver al menú") -> Dict[str, Any]:
        keyboard = telegram_service.create_inline_keyboard([[{"text": "⬅️ Volver", "callback_data": "menu"}]])
        return _wrap_payload(chat_id, text, reply_markup=keyboard)

    @staticmethod
    async def small_notice(chat_id: int, text: str) -> Dict[str, Any]:
        return _wrap_payload(chat_id, f"ℹ️ {text}")

    @staticmethod
    async def rate_limit_notice(chat_id: int) -> Dict[str, Any]:
        text = "⏳ Estamos recibiendo muchas solicitudes. Por favor intenta de nuevo en unos segundos."
        return _wrap_payload(chat_id, text)

    # ---- Helpers para generar botones dinámicos ----
    @staticmethod
    def buttons_from_pairs(pairs: List[Tuple[str, str]]) -> List[List[Dict[str, str]]]:
        """
        Convierte una lista de (texto, callback_data) a inline keyboard.
        Útil para construir teclados dinámicos.
        """
        return [[{"text": txt, "callback_data": cb}] for txt, cb in pairs]

    @staticmethod
    async def dynamic_menu_from_pairs(chat_id: int, title: str, pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        keyboard = telegram_service.create_inline_keyboard(TelegramTemplates.buttons_from_pairs(pairs))
        return _wrap_payload(chat_id, title, reply_markup=keyboard)

    # ---- Plantillas de ejemplo para integración con msg_handler ----
    @staticmethod
    async def msghandler_simple_reply(chat_id: int, text: str) -> Dict[str, Any]:
        return _wrap_payload(chat_id, text)

    @staticmethod
    async def not_authorized(chat_id: int) -> Dict[str, Any]:
        return _wrap_payload(chat_id, "🔒 No tienes permisos para realizar esta acción.")

    @staticmethod
    async def session_expired(chat_id: int) -> Dict[str, Any]:
        return _wrap_payload(chat_id, "🔁 Tu sesión expiró. Por favor inicia nuevamente con /start.")

# instancia lista para usar
telegram_templates = TelegramTemplates()


# -------------------------
# EJEMPLOS DE USO (comentados)
# -------------------------
# En tu controller / handler async:
#
# payload = await telegram_templates.main_menu(chat_id=12345, name="Bryan")
# await telegram_service.send_message(**payload)
#
# Para paginación:
# items = [f"Resultado {i}" for i in range(1, 31)]
# payload = await telegram_templates.paginated_list(chat_id=12345, title="Búsqueda", items=items, page=2, page_size=6)
# await telegram_service.send_message(**payload)
#
# Para enviar foto (usa telegram_service.send_photo):
# photo_payload = await telegram_templates.photo_message(chat_id=12345, photo_url="https://.../img.jpg", caption="Mira esto")
# await telegram_service.send_photo(**photo_payload)
