import re
from typing import List, Dict, Any
from datetime import datetime, timezone
from babel.dates import format_date
from dotenv import load_dotenv

from app.services.utils.utils_handler import payload_interactivo_lista
from .base_handler import BaseHandler
from app.database.database import set_estado_usuario, get_estado_usuario
from app.services.whatsapp_service import consulta_tramite
from app.services.whatsapp_template import (
    crear_payload_button,
    crear_payload_texto,
    mensaje_stiker,
)

load_dotenv()


class TramitesHandler(BaseHandler):
    """Seguimiento de trámites vía WhatsApp (detalle + menú en un solo mensaje)."""

    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler  # Dispatcher para reutilizar el mismo menú principal

    def get_context_name(self) -> str:
        return "tramites"

    def get_priority(self) -> int:
        return 10

    async def can_handle(self, texto: str, numero: str, user_state: dict) -> bool:
        t = (texto or "").strip().lower()
        keywords = [
            "tramite", "trámite", "tramites", "trámites", "seguimiento",
            "consulta", "consultar_tramite", "tramites-a",
            "tramites-busca-tramite", "tramites-cancelar",
            "nueva consulta", "nueva-consulta",
        ]
        return any(k in t for k in keywords)

    async def handle_message(
        self, texto: str, numero: str, name: str, msg_id: str
    ) -> List[Dict[str, Any]]:
        user_state = await get_estado_usuario(numero)
        estado = (user_state or {}).get("estado", "")
        t_raw = (texto or "").strip()
        t = t_raw.lower()

        # ---- Controles globales
        if t in {"salir", "cancelar"}:
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            if self.msg_handler and hasattr(self.msg_handler, "show_main_menu"):
                return await self.msg_handler.show_main_menu(numero, name)
            return [self._payload_servicios(numero, self._mensaje_bienvenida(name))]

        if t in {"nueva consulta", "nueva-consulta", "tramites:nueva-consulta"}:
            await set_estado_usuario(numero, {"contexto": "tramites", "estado": "tramites-a-a"})
            return [await crear_payload_button(
                numero,
                "🧾 Ingresa el *número de trámite* para una nueva consulta:",
                "",
                "salir", "Cancelar"
            )]

        if t in {"volver al inicio", "volver_inicio", "inicio:menu"}:
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            if self.msg_handler and hasattr(self.msg_handler, "show_main_menu"):
                return await self.msg_handler.show_main_menu(numero, name)
            return [self._payload_servicios(numero, self._mensaje_bienvenida(name))]

        if t in {"volver al menu catastral", "volver al menú catastral", "catastro:menu"}:
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            if self.msg_handler and hasattr(self.msg_handler, "show_main_menu"):
                return await self.msg_handler.show_main_menu(numero, name)
            return [self._payload_servicios(numero, self._mensaje_bienvenida(name))]

        # Vacíos / "." / emojis
        if t == "" or t == "." or self.contiene_emojis(t_raw):
            if estado == "tramites-a-a":
                return [await crear_payload_button(
                    numero,
                    "❗ El mensaje está vacío o no es válido.\n"
                    "Por favor ingresa el *número de trámite* (mín. 3 caracteres):",
                    "",
                    "salir", "Cancelar"
                )]
            if estado == "tramites-busca-tramite":
                return [await crear_payload_button(
                    numero,
                    "❗ La *contraseña* no es válida.\n"
                    "Por favor ingrésala nuevamente (mín. 3 caracteres):",
                    "",
                    "salir", "Cancelar"
                )]
            if self.msg_handler and hasattr(self.msg_handler, "show_main_menu"):
                return await self.msg_handler.show_main_menu(numero, name)
            return [self._payload_servicios(numero, self._mensaje_bienvenida(name))]

        # ---- Flujo
        if estado == "":
            await set_estado_usuario(numero, {"contexto": "tramites", "estado": "tramites-a-a"})
            return [
                await mensaje_stiker(numero, "1968158477348284"),
                await crear_payload_button(
                    numero,
                    f"¡Hola 😊 {name}! Bienvenido al *seguimiento de trámites*.\n"
                    "Por favor ingresa el *número de trámite*: ",
                    "",
                    "salir", "Cancelar"
                ),
            ]

        if estado == "tramites-a-a":
            if self._valido(t_raw):
                await set_estado_usuario(
                    numero,
                    {"contexto": "tramites", "estado": "tramites-busca-tramite", "numero-tramite": t_raw},
                )
                return [await crear_payload_button(
                    numero,
                    "🔐 Ahora ingresa la *contraseña del trámite*:",
                    "",
                    "salir", "Cancelar"
                )]
            return [await crear_payload_button(
                numero,
                "🚫 El número de trámite parece incorrecto.\n"
                "Debe ser alfanumérico (mín. 3). Inténtalo de nuevo:",
                "",
                "salir", "Cancelar"
            )]

        if estado == "tramites-busca-tramite":
            # (El spinner puede quedarse como mensaje aparte si quieres feedback inmediato)
            spinner = await crear_payload_texto(numero, "⏳ Estamos verificando tus datos...")
            msgs: List[Dict[str, Any]] = [spinner]

            if self._valido(t_raw):
                numero_tramite = (user_state or {}).get("numero-tramite")
                await set_estado_usuario(numero, {"contexto": "tramites", "estado": ""})

                # 👉 Detalle + opciones en UN SOLO MENSAJE (interactive list)
                detalle = await self.procesar_tramite2(numero_tramite, t_raw)
                unico = self._payload_detalle_con_menu(numero, detalle)  # <-- aquí se fusiona
                msgs.append(unico)
                return msgs

            msgs.append(await crear_payload_button(
                numero,
                "🚫 La contraseña no es válida.\n"
                "Debe ser alfanumérica (mín. 3). Inténtalo otra vez:",
                "",
                "salir", "Cancelar"
            ))
            return msgs

        # Fallback: reinicio
        await set_estado_usuario(numero, {"contexto": "", "estado": ""})
        if self.msg_handler and hasattr(self.msg_handler, "show_main_menu"):
            return await self.msg_handler.show_main_menu(numero, name)
        return [self._payload_servicios(numero, self._mensaje_bienvenida(name))]

    # ------------------ Menús ------------------
    def _payload_servicios(self, numero: str, mensaje: str) -> dict:
        """Menú principal igual al del dispatcher."""
        if self.msg_handler and hasattr(self.msg_handler, "build_seccion"):
            seccion = self.msg_handler.build_seccion("🚀 Servicios Disponibles")
            return payload_interactivo_lista(numero, mensaje, [seccion], "Ver servicios")
        return payload_interactivo_lista(numero, mensaje, self._opciones_inicio(), "Ver servicios")

    def _payload_menu_tramites(self) -> list:
        """Sección reutilizable para el menú específico de trámites."""
        return [{
            "title": "Opciones disponibles",
            "rows": [
                {"id": "tramites:nueva-consulta", "title": "Nueva consulta", "description": "Consultar otro trámite."},
                 {"id": "inicio", "title": "Volver", "description": "Menu principal."},
                
            ],
        }]

    def _payload_detalle_con_menu(self, numero: str, detalle: str) -> dict:
        """
        Arma un SOLO mensaje interactivo (LIST) donde el body contiene el detalle
        y la lista muestra las opciones.
        """
        body = self._fit_whatsapp_body(detalle + "\n\n*Opciones disponibles:*")
        secciones = self._payload_menu_tramites()
        return payload_interactivo_lista(numero, body, secciones, "Ver opciones")

    # --------------- Utilidades ---------------
    def _fit_whatsapp_body(self, text: str, limit: int = 1024) -> str:
        """
        WhatsApp LIST body tiene límite de 1024 chars.
        Cortamos con elipsis si lo supera para evitar errores 400.
        """
        text = (text or "").strip()
        return text if len(text) <= limit else (text[: limit - 1] + "…")

    def _valido(self, texto: str) -> bool:
        patron = r"^[a-zA-Z0-9\-]+$"
        return bool(re.fullmatch(patron, texto or "")) and len(texto) >= 3 and not self.contiene_emojis(texto)

    def contiene_emojis(self, texto: str) -> bool:
        emoji_pattern = re.compile(
            "[" "\U0001F600-\U0001F64F" "\U0001F300-\U0001F5FF" "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF" "\U00002702-\U000027B0" "\U000024C2-\U0001F251" "]+",
            flags=re.UNICODE,
        )
        return bool(emoji_pattern.search(texto or ""))

    @staticmethod
    def dias_desde_fecha(fecha_iso: str) -> int:
        fecha_inicial = datetime.fromisoformat((fecha_iso or "").replace("Z", "+00:00"))
        ahora = datetime.now(timezone.utc)
        return (ahora - fecha_inicial).days

    def _opciones_inicio(self) -> list:
        return [{
            "title": "🚀 Servicios Disponibles",
            "rows": [
                {"id": "igob", "title": "Recupera contraseña IGOB", "description": "¿Olvidaste tu clave? Recupérala al instante."},
                {"id": "tramites", "title": "Seguimiento de trámites", "description": "Consulta el estado de tus trámites municipales."},
                {"id": "catastro", "title": "Información catastral", "description": "Requisitos y consultas catastrales."},
                {"id": "hospitales", "title": "Hospitales municipales", "description": "Ubicaciones y servicios disponibles."},
                {"id": "ciudadano", "title": "Información ciudadana", "description": "Puntos y horarios de atención."},
                {"id": "veterinaria", "title": "Atención veterinaria", "description": "Agenda vacunas o esterilizaciones."},
                {"id": "limpieza", "title": "100 jueves de acción", "description": "Solicita limpieza y mejoras para tu barrio."},
            ],
        }]

    def _mensaje_bienvenida(self, name: str) -> str:
        bot_name = "AMI"
        organization_name = "Gobierno Autónomo Municipal de La Paz"
        return (
            f"*¡Hola!* {name} 👋 *Soy {bot_name}*, tu agente municipal inteligente del {organization_name}.\n"
            "Escríbeme algunas palabras clave sobre lo que estás buscando, por ejemplo: recuperar contraseña iGOB\n"
        )

    # -------------- Llamada al backend --------------
    async def procesar_tramite2(self, numero_tramite: str, contra_tramite: str) -> str:
        try:
            resp = await consulta_tramite({"numero": numero_tramite, "contra": contra_tramite})
            if not resp.get("estado"):
                return ("❌ No se logró identificar el trámite.\n"
                        "Verifica si el *número* o la *contraseña* son correctos y vuelve a intentarlo.")

            try:
                historial = resp["data"]["historial"]
                data_principal = resp["data"]["data_principal"]

                asunto = (data_principal.get("asunto") or "").strip()
                remitente = (data_principal.get("remitente") or "").strip()

                fecha_creacion = datetime.fromisoformat(
                    (data_principal.get("fecha_creacion") or "").replace("Z", "+00:00")
                )
                fecha_literal = format_date(fecha_creacion.date(), format="full", locale="es")

                ultimo = historial[-1] if historial else {}
                nodo = (ultimo.get("nodo_activo") or {})
                fecha_mod_str = nodo.get("fecha_iso")

                fecha_mod_literal = None
                if fecha_mod_str:
                    fecha_mod = datetime.fromisoformat(fecha_mod_str.replace("Z", "+00:00"))
                    fecha_mod_literal = format_date(fecha_mod.date(), format="full", locale="es")

                ubicacion = (
                    f"{nodo.get('nombre_nodo','(sin nodo)')} que pertenece a la "
                    f"{nodo.get('uo_sigla_descripcion','(sin unidad)')} "
                    f"({nodo.get('uo_sigla','—')})"
                )

                # —— Texto bonito, compacto (apto para body del LIST) ——
                mensaje = (
                    "👋 *Hola, {rem}*\n"
                    "📄 Trámite *{num}*\n"
                    "📝 Asunto: {asunto}\n"
                    "---------------------\n"
                    "🔎 *Detalle del seguimiento*\n"
                    "📆 Ingreso: {ingreso}\n"
                    "{ultima}"
                    "📍 Ubicación: {ubi}\n"
                    "✅ Estado: {estado} → {operador}\n"
                    "----------------------\n"
                    "⏱️ Tiempo transcurrido: *{dias} días* calendario hasta la fecha."
                ).format(
                    rem=(remitente or "contribuyente"),
                    num=numero_tramite,
                    asunto=asunto,
                    ingreso=fecha_literal,
                    ultima=(f"📆 Última actualización: {fecha_mod_literal}\n"
                            if fecha_mod_literal else
                            "📆 Última actualización: El trámite aún no ha sido recibido\n"),
                    ubi=ubicacion,
                    estado=ultimo.get("estado", "(sin estado)"),
                    operador=nodo.get("usuario_operador_nombre", "(operador no disponible)"),
                    dias=self.dias_desde_fecha(data_principal.get("fecha_creacion") or "")
                )

                return mensaje

            except Exception as err:
                print(f"❌ Error al procesar datos del trámite: {err}")
                return "❌ Ocurrió un error al procesar los datos del trámite."

        except Exception as error:
            print(f"❌ Error al consultar el trámite: {error}")
            return "❌ Ocurrió un error al consultar el trámite."
