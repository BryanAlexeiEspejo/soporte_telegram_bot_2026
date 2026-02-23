# soporte_handler.py
import os
import aiohttp
import logging
import asyncio
from typing import Any, Dict, List, Optional, Sequence, Tuple
from datetime import datetime

from app.database.database import get_estado_usuario, set_estado_usuario

# archivo de suscripciones (persistente en JSON)
from app.notifications.subscriptions_file import (
    add_subscription_file,
    remove_subscription_file,
    get_subscribers_file,
    list_all_codes,
    list_all_subscriptions_pairs,
    _get_last_states,
    _set_last_state,
    get_last_state,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SoporteHandler:
    """
    Soporte handler — versión lista para usar con suscripción automática.
    """

    DEFAULT_API_URL = "http://192.168.7.31:4001/gamlp/wsAsignacion/getAsignaciones"
    DEFAULT_API_TOKEN = "BOTAMI"

    def __init__(self, root_handler):
        self.root = root_handler
        # leer variables de entorno, con fallback
        self.api_url = os.getenv("API_GAMLP_URL") or self.DEFAULT_API_URL
        self.api_token = os.getenv("API_GAMLP_TOKEN") or self.DEFAULT_API_TOKEN

        # Reusar sesión aiohttp por instancia
        self._session = aiohttp.ClientSession()

    async def close(self):
        """Cerrar la sesión aiohttp al apagar la app"""
        try:
            await self._session.close()
        except Exception:
            logger.exception("Error cerrando session aiohttp")

    # -----------------------
    # Mensajes básicos
    # -----------------------
    def _text(self, chat_id: str, text: str) -> Dict:
        return {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    def _text_with_reply_markup(self, chat_id: str, text: str, reply_markup: Dict) -> Dict:
        return {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "reply_markup": reply_markup}

    def _menu_text(self) -> str:
        return (
            "\n\n*¿Qué deseas hacer ahora?*\n"
            "1️⃣ *Volver al menú*\n"
            "2️⃣ *Nueva consulta*\n"
            "3️⃣ *Cancelar*\n\n"
            "Responde con el número (1/2/3) o con la opción (ej: \"nueva consulta\")."
        )

    # -----------------------
    # Botonera INLINE segura
    # -----------------------
    def _build_inline_buttons(self, buttons: Sequence[Tuple[str, str]]) -> Dict:
        row = []
        for label, token in buttons:
            token_clean = str(token).replace(" ", "_")
            if len(token_clean) > 64:
                token_clean = token_clean[:64]
                logger.warning("callback_data truncated to 64 chars")
            row.append({"text": label, "callback_data": token_clean})
        return {"inline_keyboard": [row]}

    def _buttons_message(self, chat_id: str, text: str, buttons: Sequence[Tuple[str, str]]) -> Dict:
        reply_markup = self._build_inline_buttons(buttons)
        return self._text_with_reply_markup(chat_id, text, reply_markup)

    # -----------------------
    # Can handle
    # -----------------------
    async def can_handle(self, texto_id: str, numero: str, user_state: dict) -> bool:
        texto_id = (texto_id or "").lower().strip()
        if texto_id == "soporte":
            return True
        if user_state.get("estado") in ("soporte_buscar_activo", "soporte_menu", "suscrito"):
            return True
        return False

    # -----------------------
    # Main handler
    # -----------------------
    async def handle_message(self, texto: Any, numero: str, name: str, msg_id: str = "") -> List[Dict]:
        texto_plano = self.root._force_extract_raw_text(texto).strip()
        user_state = await get_estado_usuario(numero) or {}
        estado = user_state.get("estado", "")

        # comando inicial: "soporte"
        if texto_plano.lower() == "soporte":
            quien = name or "usuario"
            if user_state.get("estado") == "suscrito":
                bienvenida = (
                    f"👋 *Hola {self._escape_md(quien)}!*\n\n"
                    "Bienvenido al *módulo de SOPORTE*.\n"
                    "Ya estás suscrito a notificaciones para tu código. Si deseas consultar otro código, escribe el código o pulsa *🔎 Nueva consulta*."
                )
                botones = [
                    ("🔔 Mis suscripciones", "mis_suscripciones"),
                    ("🔎 Nueva consulta", "nueva_consulta"),
                    ("🏠 Menú principal", "inicio")
                ]
                return [self._text(numero, bienvenida), self._buttons_message(numero, "Selecciona una opción:", botones)]

            # NUEVO: Mensaje simplificado pedido por ti
            await set_estado_usuario(numero, {**user_state, "estado": "soporte_buscar_activo"})
            bienvenida = (
                f"👋 *Hola {self._escape_md(quien)}!*\n\n"
                "Bienvenido al *módulo de SOPORTE*.\n\n"
                "➡️ Proporciona el *CÓDIGO DE FORMULARIO* o el *TICKET*."
            )
            return [self._text(numero, bienvenida)]

        # cuando estamos pidiendo el codigo
        if estado == "soporte_buscar_activo":
            return await self._buscar_activo(numero, texto_plano)

        # interceptamos DESUSCRIBIR y menú si estamos en menu/suscrito
        if estado in ("soporte_menu", "suscrito"):
            text_strip = texto_plano.strip()

            # DESUSCRIBIR <CODIGO>
            if text_strip.upper().startswith("DESUSCRIBIR"):
                parts = text_strip.split(maxsplit=1)
                if len(parts) < 2:
                    return [self._text(numero, "Debes enviar: `DESUSCRIBIR <CODIGO>`")]
                codigo_a = parts[1].strip()
                removed = await remove_subscription_file(codigo_a, numero)
                if removed:
                    us = await get_estado_usuario(numero) or {}
                    if us.get("codigo") == codigo_a:
                        await set_estado_usuario(numero, {"estado": "", "codigo": None})
                    return [self._text(numero, f"✅ Te desuscribí de las notificaciones para `{codigo_a}`.")]
                else:
                    return [self._text(numero, f"No estabas suscrito al código `{codigo_a}`.")]

            return await self._handle_menu_choice(numero, texto_plano)

        return [self._text(numero, "❓ Opción no válida. Escribe *soporte* para iniciar.")]

    # -----------------------
    # Manejo elección menú / callbacks
    # -----------------------
    async def _handle_menu_choice(self, numero: str, texto: str) -> List[Dict]:
        t_raw = (texto or "").strip()
        t = t_raw.lower()

        user_state = await get_estado_usuario(numero) or {}

        if t in ("inicio", "soporte_volver_menu", "1", "volver", "volver al menu", "volver al menú", "menu"):
            try:
                if hasattr(self.root, "show_main_menu"):
                    await self.root.show_main_menu(numero)
                    if user_state.get("estado") != "suscrito":
                        await set_estado_usuario(numero, {"estado": ""})
                    return []
            except Exception:
                logger.exception("Error al llamar show_main_menu")
            if user_state.get("estado") != "suscrito":
                await set_estado_usuario(numero, {"estado": ""})
            return [self._text(numero, "🔙 Volviendo al menú principal...")]

        if t in ("nueva_consulta", "soporte_nueva_consulta", "2", "nueva consulta", "consultar", "buscar", "nuevo"):
            new_state = {**user_state, "estado": "soporte_buscar_activo"}
            await set_estado_usuario(numero, new_state)
            # MENSAJE EXACTO pedido por ti
            return [self._text(numero, "🔎 Proporciona el *CÓDIGO DE FORMULARIO* o el *TICKET*:")]

        if t in ("3", "cancelar", "salir"):
            if user_state.get("estado") != "suscrito":
                await set_estado_usuario(numero, {"estado": ""})
            else:
                await set_estado_usuario(numero, user_state)
            return [self._text(numero, "❌ Operación cancelada. Si deseas volver a consultar escribe *soporte*.")]

        botones = [
            ("🔎 Nueva consulta", "nueva_consulta"),
            ("🏠 Volver al menú", "inicio")
        ]
        return [
            self._text(numero, "No entendí la opción. Por favor responde con 1, 2 o 3."),
            self._buttons_message(numero, "Selecciona una opción:", botones)
        ]

    # -----------------------
    # Consumir API GAMLP
    # -----------------------
    async def _fetch_asignaciones(self) -> Optional[List[Dict]]:
        if not self.api_url or not self.api_token:
            logger.error("API_GAMLP_URL o API_GAMLP_TOKEN no configurado")
            return None

        headers = {"Authorization": f"Bearer {self.api_token}", "Accept": "application/json"}
        try:
            async with self._session.get(self.api_url, headers=headers, timeout=20) as resp:
                if resp.status != 200:
                    logger.error("API GAMLP respondió %s", resp.status)
                    try:
                        txt = await resp.text()
                        logger.debug("Respuesta API (no 200): %s", txt)
                    except Exception:
                        pass
                    return None
                data = await resp.json()
                if isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], list):
                        return data["data"]
                    return [data]
                if isinstance(data, list):
                    return data
                return []
        except aiohttp.ClientError:
            logger.exception("ClientError llamando API GAMLP")
            return None
        except asyncio.TimeoutError:
            logger.exception("Timeout llamando API GAMLP")
            return None
        except Exception:
            logger.exception("Error llamando API GAMLP")
            return None

    # -----------------------
    # Buscar activo
    # -----------------------
    async def _buscar_activo(self, numero: str, codigo: str) -> List[Dict]:
        asignaciones = await self._fetch_asignaciones()
        if not asignaciones:
            await set_estado_usuario(numero, {"estado": "soporte_buscar_activo"})
            return [self._text(numero, "❌ No se pudo obtener información del sistema. Intenta nuevamente más tarde.")]

        codigo = str(codigo).strip()
        encontrado = next(
            (
                a for a in asignaciones
                if str(a.get("codigo_formulario", "")).strip() == codigo
                or str(a.get("codigo_form", "")).strip() == codigo
                or str(a.get("codigo_activo", "")).strip() == codigo
                or str(a.get("codigoActiva", "")).strip() == codigo
                or str(a.get("codigo", "")).strip() == codigo
            ),
            None
        )

        if not encontrado:
            await set_estado_usuario(numero, {"estado": "soporte_buscar_activo"})
            return [self._text(numero, f"🔍 No se encontró el código *{self._escape_md(codigo)}*.\n\nPor favor verifica y vuelve a intentarlo, o responde *3* para cancelar.")]

        # extraer estado actual del formulario (campo puede variar)
        estado_actual = encontrado.get("estado_formulario") or encontrado.get("estado") or "DESCONOCIDO"

        # SUSCRIPCIÓN AUTOMÁTICA: añadir al archivo de subscriptions
        try:
            await add_subscription_file(str(codigo), numero)
        except Exception:
            logger.exception("Error agregando suscripción automática para %s / %s", codigo, numero)

        # Guardamos en la sesión del chat el código y el último estado visto.
        await set_estado_usuario(numero, {"estado": "suscrito", "codigo": codigo, "ultimo_estado": estado_actual})

        info_msg = self._formatear_activo(encontrado)

        # Botones SIN "Notificarme"
        botones = [
            ("🔎 Nueva consulta", "nueva_consulta"),
            ("🏠 Volver al menú", "inicio")
        ]
        return [
            self._text(numero, info_msg + "\n\n✅ LISTO — Se te ha suscrito automáticamente para recibir notificaciones por este código."),
            self._buttons_message(numero, "Selecciona una opción:", botones)
        ]

    # -----------------------
    # Utilities
    # -----------------------
    def _parse_date(self, iso: Optional[str]) -> str:
        if not iso:
            return "-"
        try:
            if iso.endswith("Z"):
                iso = iso.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return iso

    def _escape_md(self, text: Optional[str]) -> str:
        if text is None:
            return "-"
        text = str(text)
        for ch in "_*[]()~`>#+-=|{}.!":
            text = text.replace(ch, f"\\{ch}")
        return text

    def _formatear_activo(self, a: Dict) -> str:
        codigo_form = a.get("codigo_formulario") or a.get("codigo_form") or a.get("codigoFormulario") or a.get("codigo") or "-"
        estado = a.get("estado_formulario") or a.get("estado") or "-"
        diagnostico = a.get("diagnostico_previo") or a.get("diagnostico") or "-"
        fecha = self._parse_date(a.get("fecha_solicitud") or a.get("fechaAsignacion") or a.get("fecha") or "")
        codigo_activo = a.get("codigo_activo") or a.get("codigo_act") or "-"
        nombre_fun = " ".join(filter(None, [a.get("nombre_funcionario"), a.get("paterno_fun"), a.get("materno_fun")])) or a.get("nombre_funcionario") or "-"
        carnet = a.get("carnet_fun") or a.get("carnet") or "-"
        celular = a.get("celular_fun") or a.get("celular") or "-"
        correo = a.get("correo_fun") or a.get("correo") or "-"
        tipo_atencion = a.get("tipo_atencion") or a.get("tipoAtencion") or "-"
        unidad = a.get("nombre_uo") or a.get("unidadDestino") or "-"
        ubicacion = a.get("ubicacion") or "-"
        msg = (
            "📄 *INFORMACIÓN DEL FORMULARIO / ACTIVO*\n\n"
            f"🆔 Código formulario: `{self._escape_md(str(codigo_form))}`\n"
            f"🆔 Código activo: `{self._escape_md(str(codigo_activo))}`\n"
            f"📌 Estado: *{self._escape_md(str(estado))}*\n"
            f"📅 Fecha solicitud: {self._escape_md(fecha)}\n\n"
            f"👤 Funcionario: {self._escape_md(nombre_fun)}\n"
            f"🆔 Carnet: {self._escape_md(str(carnet))}\n"
            f"📞 Celular: {self._escape_md(str(celular))}\n"
            f"✉️ Correo: {self._escape_md(str(correo))}\n\n"
            f"🏢 Unidad: {self._escape_md(unidad)}\n"
            f"📍 Ubicación: {self._escape_md(ubicacion)}\n"
            f"🛠️ Tipo atención: {self._escape_md(tipo_atencion)}\n\n"
            f"📝 Diagnóstico previo:\n`{self._escape_md(str(diagnostico))}`"
        )
        return msg


# -----------------------
# Watcher: verificar cambios y notificar (helper)
# -----------------------
async def watch_subscriptions(
    handler: SoporteHandler,
    send_message_callable,
    poll_interval: int = 60,
    codes_to_watch: Optional[List[str]] = None
):
    # (Dejar igual que tu implementación actual. start_subscription_watcher usa esta función.)
    if not hasattr(handler, "_fetch_asignaciones"):
        logger.error("handler no tiene _fetch_asignaciones")
        return

    while True:
        try:
            asignaciones = await handler._fetch_asignaciones()
            if not asignaciones:
                await asyncio.sleep(poll_interval)
                continue

            current_map = {}
            for a in asignaciones:
                cod = str(a.get("codigo_formulario") or a.get("codigo_form") or a.get("codigo") or "").strip()
                if not cod:
                    continue
                estado = a.get("estado_formulario") or a.get("estado") or None
                current_map[cod] = str(estado) if estado is not None else None

            if codes_to_watch:
                codes_list = set(codes_to_watch)
            else:
                codes_list = set(await list_all_codes())

            for codigo in codes_list:
                codigo = str(codigo)
                estado_actual = current_map.get(codigo)
                ultimo = await get_last_state(codigo)
                if estado_actual != ultimo:
                    subs = await get_subscribers_file(codigo)
                    if subs:
                        text = (
                            f"🔔 *Actualización del estado* para el código `{codigo}`:\n\n"
                            f"Estado anterior: `{ultimo or '—'}`\n"
                            f"Estado actual: `{estado_actual or '—'}`\n\n"
                            "Si deseas dejar de recibir estas notificaciones responde:\n"
                            f"`DESUSCRIBIR {codigo}`"
                        )
                        for chat in subs:
                            try:
                                maybe_await = send_message_callable(chat, text, None)
                                if asyncio.iscoroutine(maybe_await):
                                    await maybe_await
                            except Exception:
                                logger.exception("Error enviando notificación a %s para codigo %s", chat, codigo)

                    await _set_last_state(codigo, estado_actual)

        except Exception:
            logger.exception("Error en watch_subscriptions")
        await asyncio.sleep(poll_interval)


def start_subscription_watcher(root_handler, send_message_callable, poll_interval: int = 60):
    handler = SoporteHandler(root_handler)
    loop = asyncio.get_event_loop()
    loop.create_task(watch_subscriptions(handler, send_message_callable, poll_interval))
    logger.info("Watcher de suscripciones iniciado (poll_interval=%s)", poll_interval)
