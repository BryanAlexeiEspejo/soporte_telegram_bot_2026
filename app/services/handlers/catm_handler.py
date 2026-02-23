from __future__ import annotations

import os
from typing import Any, Dict, List

from app.services.handlers.base_handler import BaseHandler
from app.database.database import set_estado_usuario, get_estado_usuario
from app.database.database import registrar_historial
from app.services.utils.utils_handler import payload_interactivo_lista
from app.services.handlers.atm.menu_atm import obtener_opciones_atm



class CatmHandler(BaseHandler):
    """Handler MENÚ ATM (Administración Tributaria Municipal – Ley 573)"""

    def __init__(self, msg_handler=None):
        super().__init__()
        self.msg_handler = msg_handler
        self._keywords = {"atm", "alivio", "alivio tributario", "impuesto", "impuestos", "tributario"}

    def get_context_name(self) -> str:
        return "atm"

    def get_priority(self) -> int:
        return 100

    async def can_handle(self, texto: Any, numero: str, user_state: dict) -> bool:
        t = self._extraer_texto_id(texto).strip().lower()
        ctx = (user_state or {}).get("contexto", "")
        est = (user_state or {}).get("estado", "")
        return (
            ctx == "atm"
            or (isinstance(est, str) and est.startswith("atm"))
            or t == "atm"
            or t.startswith("atm-")
            or t.startswith("q-atm-")
            or any(k in t for k in self._keywords)
        )

    # ---- UI helpers ----
    def _payload_texto(self, numero: str, body: str) -> Dict[str, Any]:
        return {"messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": body}}

    def _menu_atm(self, numero: str, name: str) -> Dict[str, Any]:
        bot = os.getenv("BOT_NAME", "AMI")
        cuerpo = (
            f"👋 ¡Hola {name}!.\nBienvenidos a la Administración Tributaria Municipal - ATM.\nAquí verás información del Perdonazo Tributario, deudas, pagos.\n\n✅ Ya iniciamos el cobro de impuestos municipales con el: 15% de descuento gestión 2025.\n"
           
            "\n*Selecciona una de las opciones:*"
        )
        secciones = obtener_opciones_atm()
        secciones[0]["rows"].append({
            "id": "inicio",
            "title": "⬅️ Volver al inicio",
            "description": "Regresar al menú principal.",
        })
        # ⚠️ Usa POSICIONALES (no kwargs)
        return payload_interactivo_lista(numero, cuerpo, secciones, "Menú ATM")

    # ---- flujo principal ----
    async def handle_message(self, texto: Any, numero: str, name: str, msg_id: str = "") -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]] = []
        user_state = await get_estado_usuario(numero) or {}
        estado = user_state.get("estado", "")
        t = self._extraer_texto_id(texto).strip().lower()
            # 🔹 REGISTRO GLOBAL DE TODO (texto, botones, listas)
        # try:
        #     await registrar_historial(
        #         tipo="entrada_usuario",
        #         numero=numero,
        #         texto=str(texto)
        #     )
        # except Exception as e:
        #     # no rompe el flujo del bot
        #     print("⚠️ Error guardando historial:", e)


        if t == "inicio":
            await set_estado_usuario(numero, {"contexto": "", "estado": ""})
            data.append(self._payload_texto(numero, "😌 Listo, volvimos al menú principal."))
            return data

        if estado == "" or t in {"atm", "atm-menu"}:
            await set_estado_usuario(numero, {"contexto": "atm", "estado": "esperando-opcion"})
            data.append(self._menu_atm(numero, name))
            return data

        # 1) LEY
        if (estado == "esperando-opcion" and t == "atm-1") or t == "atm-1":
            from app.services.handlers.atm.A_1_ley_alivio_tributario import manejar_ley_alivio_573
            data.extend(await manejar_ley_alivio_573(numero)); return data

        if t == "q-atm-1-1":
            from app.services.handlers.atm.A_1_1_pregunta_1 import manejar_A_1_1_respuesta
            data.extend(await manejar_A_1_1_respuesta(numero)); return data
        if t == "q-atm-1-2":
            from app.services.handlers.atm.A_1_2_pregunta_1 import manejar_A_1_2_respuesta
            data.extend(await manejar_A_1_2_respuesta(numero)); return data
        if t == "q-atm-1-3":
            from app.services.handlers.atm.A_1_3_pregunta_1 import manejar_A_1_3_respuesta
            data.extend(await manejar_A_1_3_respuesta(numero)); return data
        if t == "q-atm-1-4":
            from app.services.handlers.atm.A_1_4_pregunta_1 import manejar_A_1_4_respuesta
            data.extend(await manejar_A_1_4_respuesta(numero)); return data

        # 2) ALCANCE Y BENEFICIOS
        if (estado == "esperando-opcion" and t == "atm-2") or t == "atm-2":
            from app.services.handlers.atm.A_2_Alcance_beneficios_alivio import manejar_alcance_beneficios_alivio
            data.extend(await manejar_alcance_beneficios_alivio(numero)); return data

        if t == "q-atm-2-1":
            from app.services.handlers.atm.A_2_1_pregunta_2 import manejar_A_2_1_respuesta
            data.extend(await manejar_A_2_1_respuesta(numero)); return data
        if t == "q-atm-2-2":
            from app.services.handlers.atm.A_2_2_pregunta_2 import manejar_A_2_2_respuesta
            data.extend(await manejar_A_2_2_respuesta(numero)); return data
        if t == "q-atm-2-3":
            from app.services.handlers.atm.A_2_3_pregunta_2 import manejar_A_2_3_respuesta
            data.extend(await manejar_A_2_3_respuesta(numero)); return data
        if t == "q-atm-2-4":
            from app.services.handlers.atm.A_2_4_pregunta_2 import manejar_A_2_4_respuesta
            data.extend(await manejar_A_2_4_respuesta(numero)); return data

        # 3) FORMAS Y LUGARES DE PAGO
        if (estado == "esperando-opcion" and t == "atm-3") or t == "atm-3":
            from app.services.handlers.atm.A_3_formas_lugares_pago import manejar_formas_lugares_pago
            data.extend(await manejar_formas_lugares_pago(numero)); return data

        if t == "q-atm-3-1":
            from app.services.handlers.atm.A_3_1_pregunta_3 import manejar_A_3_1_respuesta
            data.extend(await manejar_A_3_1_respuesta(numero)); return data
        if t == "q-atm-3-2":
            from app.services.handlers.atm.A_3_2_pregunta_3 import manejar_A_3_2_respuesta
            data.extend(await manejar_A_3_2_respuesta(numero)); return data
        if t == "q-atm-3-3":
            from app.services.handlers.atm.A_3_3_pregunta_3 import manejar_A_3_3_respuesta
            data.extend(await manejar_A_3_3_respuesta(numero)); return data
        if t == "q-atm-3-4":
            from app.services.handlers.atm.A_3_4_pregunta_3 import manejar_A_3_4_respuesta
            data.extend(await manejar_A_3_4_respuesta(numero)); return data
        if t == "q-atm-3-5":
            from app.services.handlers.atm.A_3_5_pregunta_3 import manejar_A_3_5_respuesta
            data.extend(await manejar_A_3_5_respuesta(numero)); return data
        if t == "q-atm-3-6":
            from app.services.handlers.atm.A_3_6_pregunta_3 import manejar_A_3_6_respuesta
            data.extend(await manejar_A_3_6_respuesta(numero)); return data
        if t == "q-atm-3-7":
            from app.services.handlers.atm.A_3_7_pregunta_3 import manejar_A_3_7_respuesta
            data.extend(await manejar_A_3_7_respuesta(numero)); return data

        if t == "q-atm-3-8":
            from app.services.handlers.atm.A_3_8_pregunta_3 import manejar_A_3_8_respuesta
            data.extend(await manejar_A_3_8_respuesta(numero)); return data

        # 4) CASOS ESPECIALES
        if (estado == "esperando-opcion" and t == "atm-4") or t == "atm-4":
            from app.services.handlers.atm.A_4_casos_especiales import manejar_casos_especiales
            data.extend(await manejar_casos_especiales(numero)); return data
        if t == "q-atm-4-1":
            from app.services.handlers.atm.A_4_1_pregunta_4 import manejar_A_4_1_respuesta
            data.extend(await manejar_A_4_1_respuesta(numero)); return data

        # 5) SANCIONES Y EFECTOS
        if (estado == "esperando-opcion" and t == "atm-5") or t == "atm-5":
            from app.services.handlers.atm.A_5_consecuencias_sanciones import manejar_consecuencias_sanciones
            data.extend(await manejar_consecuencias_sanciones(numero)); return data
        if t == "q-atm-5-1":
            from app.services.handlers.atm.A_5_1_pregunta_5 import manejar_A_5_1_respuesta
            data.extend(await manejar_A_5_1_respuesta(numero)); return data

        # 6) ATENCIÓN Y SOPORTE
        if (estado == "esperando-opcion" and t == "atm-6") or t == "atm-6":
            try:
                from app.services.handlers.atm.A_6_atencion_y_soporte import manejar_atencion_y_soporte
            except ModuleNotFoundError:
                from app.services.handlers.atm.A_6_atención_y_soporte import manejar_atencion_y_soporte
            data.extend(await manejar_atencion_y_soporte(numero)); return data
        if t == "q-atm-6-1":
            try:
                from app.services.handlers.atm.A_6_1_atencion_y_soporte import manejar_A_6_1_respuesta
            except ModuleNotFoundError:
                from app.services.handlers.atm.A_6_1_atención_y_soporte import manejar_A_6_1_respuesta
            data.extend(await manejar_A_6_1_respuesta(numero)); return data

        if t == "q-atm-6-2":
            try:
                from app.services.handlers.atm.A_6_2_atencion_y_soporte import manejar_A_6_2_respuesta
            except ModuleNotFoundError:
                from app.services.handlers.atm.A_6_2_atención_y_soporte import manejar_A_6_2_respuesta
            data.extend(await manejar_A_6_2_respuesta(numero)); return data

        if t == "q-atm-6-3":
            try:
                from app.services.handlers.atm.A_6_3_atencion_y_soporte import manejar_A_6_3_respuesta
            except ModuleNotFoundError:
                from app.services.handlers.atm.A_6_3_atención_y_soporte import manejar_A_6_3_respuesta
            data.extend(await manejar_A_6_3_respuesta(numero)); return data

        if t == "q-atm-6-4":
            try:
                from app.services.handlers.atm.A_6_4_atencion_y_soporte import manejar_A_6_4_respuesta
            except ModuleNotFoundError:
                from app.services.handlers.atm.A_6_4_atención_y_soporte import manejar_A_6_4_respuesta
            data.extend(await manejar_A_6_4_respuesta(numero)); return data
            
            # 7) CONSULTA TU DEUDA
        if (estado == "esperando-opcion" and t == "atm-7") or t == "atm-7":
            from app.services.handlers.atm.A_7_consulta_deuda import manejar_consulta_deuda
            data.extend(await manejar_consulta_deuda(numero)); return data
        # 8) FACILIDAD DE PAGO -> ir directo al detalle (A_8_1_pregunta_1)
        if (estado == "esperando-opcion" and t == "atm-8") or t == "atm-8":
            from app.services.handlers.atm.A_8_1_pregunta_1 import manejar_A_8_1_respuesta
            data.extend(await manejar_A_8_1_respuesta(numero)); return data

        # 9) COBRO DE IMPUESTOS
        if (estado == "esperando-opcion" and t == "atm-9") or t == "atm-9":
            from app.services.handlers.atm.A_9_cobro_impuestos_2025 import manejar_cobro_impuestos_2025
            data.extend(await manejar_cobro_impuestos_2025(numero))
            return data

        # volver al menú ATM
        if t == "atm-menu":
            await set_estado_usuario(numero, {"contexto": "atm", "estado": "esperando-opcion"})
            data.append(self._menu_atm(numero, name)); return data

        # fallback
        data.append(self._payload_texto(numero, "No entendí tu solicitud. Elige una opción del menú *ATM – Ley 573*."))
        await set_estado_usuario(numero, {"contexto": "atm", "estado": "esperando-opcion"})
        data.append(self._menu_atm(numero, name))
        return data

    # helper: extraer id de listas/botones
    def _extraer_texto_id(self, texto: Any) -> str:
        if isinstance(texto, dict) and texto.get("type") == "interactive":
            inter = texto.get("interactive", {})
            if inter.get("type") == "list_reply":
                return inter["list_reply"]["id"]
            if inter.get("type") == "button_reply":
                return inter["button_reply"]["id"]
        return str(texto or "")
