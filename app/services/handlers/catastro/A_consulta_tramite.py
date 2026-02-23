# -*- coding: utf-8 -*-
import re
import socket
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from babel.dates import format_date
from urllib.parse import urlparse, quote_plus

from app.database.database import set_estado_usuario, get_estado_usuario
from app.services.whatsapp_service import consulta_tramite
from app.services.whatsapp_template import (
    crear_payload_texto,
    crear_payload_button,
    crear_payload_lista,
)

# --- Ajustes/constantes ---
DEFAULT_MAP_LINK = "https://maps.app.goo.gl/XQtRE17M7SnFHT596"
MAPS_FOR_PLATFORM = {
    "CAMACHO": {
        "link": "https://maps.app.goo.gl/XQtRE17M7SnFHT596",
        "instrucciones": (
            "Pase por la PIAC CAMACHO, la plataforma integral de atención ciudadana Camacho, "
            "en la av. Camacho, centro comercial camacho nivel 1."
        ),
    },
    "MIRAFLORES": {
        "link": "https://maps.app.goo.gl/NaVxPoiWucsRgSdR9",
        "instrucciones": (
            "Pase por la PLATAFORMA INTEGRAL MIRAFLORES, diríjase a la entrada de la plataforma."
        ),
    },
    "SUR": {
        "link": "https://maps.app.goo.gl/aQmGUZ74HzjqwssS9",
        "instrucciones": (
            "Pase por la PLATAFORMA INTEGRAL SUR, diríjase a la oficina de atención correspondiente."
        ),
    },
}
DEFAULT_INSTRUCCIONES = (
    "Pase por la PIAC CAMACHO, la plataforma integral de atención ciudadana Camacho, "
    "en la av. Camacho, centro comercial camacho nivel 1."
)

OFFICIAL_HOST = "sitram247iconsulta.lapaz.bo"
OFFICIAL_PATH = "/sigueTuTramite/view/autenticacion/"

# nombres que consideramos 'plataformas' y nombres administrativos
PLATFORM_KEYWORDS = ("PLATAFORMA INTEGRAL", "MIRAFLORES", "CAMACHO", "SUR")
ADMIN_KEYWORDS = ("ASISTENTE ADMINISTRATIVO", "APOYO ADMINISTRATIVO", "ASISTENTE", "APOYO")

# -------------------------


def obtener_opciones_catastro() -> list:
    return [
        {
            "title": "📚 Servicios catastrales",
            "rows": [
                {"id": "catastro-a", "title": "Consulta trámite", "description": "👉 Ver en qué estado se encuentra tu trámite catastral."},
                {"id": "inicio", "title": "Volver al inicio", "description": "Regresar al menú principal."},
            ],
        }
    ]


def opciones_postconsulta() -> list:
    return [
        {
            "title": "Opciones disponibles",
            "rows": [
                {"id": "catastro-a", "title": "Nueva consulta", "description": "Consultar otro trámite catastral."},
                {"id": "catastro", "title": "Volver al menú catastral", "description": "Abrir Servicios catastrales."},
                {"id": "inicio", "title": "Volver al inicio", "description": "Regresar al menú principal."},
            ],
        }
    ]


CANCEL_KEYWORDS = {"salir", "cancelar"}


def _valido(texto: str) -> bool:
    patron = r"^[a-zA-Z0-9\-]+$"
    return bool(re.fullmatch(patron, texto or "")) and len(texto or "") >= 3 and not _contiene_emojis(texto or "")


def _contiene_emojis(texto: str) -> bool:
    emoji_pattern = re.compile(
        "[" "\U0001F600-\U0001F64F" "\U0001F300-\U0001F5FF" "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF" "\U00002702-\U000027B0" "\U000024C2-\U0001F251" "]+",
        flags=re.UNICODE,
    )
    return bool(emoji_pattern.search(texto or ""))


def _fit_whatsapp_body(text: str, limit: int = 1024) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[:limit]


# Network helpers (sin cambios funcionales)
def _probe_host(hostname: str, port: int, timeout: float = 0.9) -> bool:
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except Exception:
        return False


def _select_scheme_for_host(hostname: str) -> str:
    try:
        if _probe_host(hostname, 443):
            return "https"
        if _probe_host(hostname, 80):
            return "http"
    except Exception:
        pass
    return "https"


# --- Historial / nodo / semáforo helpers ---


def _parse_fecha_corta(fecha_str: Optional[str]) -> Optional[datetime]:
    if not fecha_str:
        return None
    try:
        return datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
    except Exception:
        pass
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y, %H:%M:%S")
    except Exception:
        pass
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        pass
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception:
        pass
    return None


def _obtener_fecha_fila(h: dict) -> datetime:
    for k in ("fecha_iso", "fecha_recepcion", "fecha_envio"):
        v = h.get(k)
        dt = _parse_fecha_corta(v)
        if dt:
            return dt
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def _limpiar_asunto(asunto_raw: Optional[str]) -> str:
    s = (asunto_raw or "").strip()
    if not s or re.fullmatch(r"^[\W_]+$", s) or set(s) <= {".", " ", "·", ","}:
        return "Sin asunto"
    return s


def _es_url_privada(url: str) -> bool:
    if not url:
        return True
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return True
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            return True
        if hostname.startswith("192.168.") or hostname.startswith("10.") or hostname.startswith("127."):
            return True
        if hostname.startswith("172."):
            try:
                second = int(hostname.split(".")[1])
                if 16 <= second <= 31:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return True


def _buscar_en_texto_urls_maps(texto: str) -> Optional[str]:
    if not texto:
        return None
    url_regex = re.compile(r"(https?://[^\s]+)")
    for m in url_regex.findall(texto):
        candidate = m.rstrip(".,);:]\"'")
        if "maps.app" in candidate or "google.com/maps" in candidate or "goo.gl/maps" in candidate or "maps.google" in candidate:
            return candidate
    return None


def _buscar_map_link(historial: List[dict], nodo_activo: dict, data: dict) -> Optional[str]:
    # Preferir enlaces del nodo mostrado, luego data, luego historial.
    if nodo_activo:
        for key in ("maps_link", "como_llegar", "direccion_google_maps", "map_url"):
            v = nodo_activo.get(key)
            if isinstance(v, str):
                candidate = _buscar_en_texto_urls_maps(v)
                if candidate and not _es_url_privada(candidate):
                    return candidate

    if data:
        for key in ("como_llegar", "maps_link", "mapa", "instrucciones"):
            v = data.get(key) if isinstance(data, dict) else None
            if isinstance(v, str):
                candidate = _buscar_en_texto_urls_maps(v)
                if candidate and not _es_url_privada(candidate):
                    return candidate

    if historial:
        for h in reversed(historial):
            dlist = h.get("detalle_url") or []
            if isinstance(dlist, list):
                for item in dlist:
                    if isinstance(item, dict):
                        path = (item.get("path") or "").strip()
                        if path:
                            path_sanitized = path.rstrip(".,);:]\"'")
                            if not _es_url_privada(path_sanitized) and ("maps.app" in path_sanitized or "google.com/maps" in path_sanitized or "goo.gl/maps" in path_sanitized):
                                return path_sanitized
            for key in ("descripcion_proveido", "observacion", "descripcion"):
                txt = h.get(key) or ""
                if isinstance(txt, str):
                    candidate = _buscar_en_texto_urls_maps(txt)
                    if candidate and not _es_url_privada(candidate):
                        return candidate
    return None


def _nodo_es_plataforma_finalizados_o_observados(nodo: Optional[dict]) -> Tuple[bool, bool]:
    """
    Devuelve (es_finalizados_plataforma, es_observados_plataforma)
    Detecta si un nodo es 'FINALIZADOS PLATAFORMA ...' o 'OBSERVADOS PLATAFORMA ...' (robusto).
    """
    if not nodo or not isinstance(nodo, dict):
        return False, False
    name = ((nodo.get("nombre_nodo") or nodo.get("nodo") or "")).upper()
    is_plataforma = "PLATAFORMA" in name
    is_finalizados = is_plataforma and "FINALIZ" in name
    is_observados = is_plataforma and "OBSERV" in name
    return is_finalizados, is_observados


def determinar_semaforo_texto(estado_field: str, descripcion_proveido_ultimo: str, nodo_nombre: str = "", fila_real: Optional[dict] = None) -> Tuple[str, str]:
    """
    Reglas ajustadas:
    - CERR* -> ⚪ (cerrado)
    - FINALIZ* / ENTREG* -> 🟢 (finalizado)
    - OBSERV* -> 🟢 (observado)
    - POR RECIB* -> 🟡 (por recibir)  -> mostramos nodo previo
    - RECIB* / RECEPCION* -> normalmente 🔴 (recepcionado -> en cola), pero:
        * si la fila actual tiene estado_paso_detalle ACTIVO o posicion 'tramite_actual' -> 🟡 (está en curso)
        * si el nodo indica 'FINALIZADOS' o 'ENTREGA' -> 🟢
    - ENTRANTE -> 🟡 (mostramos previo)
    - defecto -> 🟡
    """
    ef = (estado_field or "").upper()
    dp = (descripcion_proveido_ultimo or "").upper()
    nn = (nodo_nombre or "").upper()

    if "CERR" in ef or "CERR" in dp or "FECHA DE CIERRE" in ef or "FECHA DE CIERRE" in dp:
        return "⚪", "Tu trámite está cerrado."

    if any(k in ef for k in ("FINALIZ", "FINALIZAD", "FINALIZADO", "ENTREG", "ENTREGA")) or any(
        k in dp for k in ("FINALIZ", "FINALIZAD", "FINALIZADO", "ENTREG", "ENTREGA")
    ) or any(x in nn for x in ("FINALIZADOS", "PARA ENTREGA", "ENTREGA")):
        return "🟢", "Tu trámite ha finalizado."

    if "OBSERV" in ef or "OBSERV" in dp or "OBSERVACI" in dp:
        return "🟡", "Tu trámite está observado y requiere atención."

    if any(x in ef for x in ("POR RECIB", "PORRECIB", "POR RECIBIR", "PORRECIBIR")) or any(
        x in dp for x in ("POR RECIB", "PORRECIB")
    ):
        return "🟡", "Tu trámite está por recibirse."

    # ENTRANTE explicit
    if "ENTRANT" in ef or (fila_real and ((fila_real.get("estado") or "").upper() == "ENTRANTE")):
        return "🟡", "Tu trámite está en proceso.\n"

    # RECIBIDO/RECEPCION
    if "RECIB" in ef or "RECEPCION" in ef or "RECEPCIONAD" in ef or "RECIBIDO" in ef:
        # si el nodo sugiere finalizado/entrega, marcar verde
        if any(x in nn for x in ("FINALIZADOS", "ENTREGA", "PARA ENTREGA")):
            return "🟢", "Tu trámite ha finalizado."

        # excepción: si la fila actual está ACTIVA o es 'tramite_actual', tratar como EN PROCESO (🟡)
        try:
            if fila_real and isinstance(fila_real, dict):
                estado_paso = (fila_real.get("estado_paso_detalle") or "").upper()
                posicion = (fila_real.get("posicion") or "").lower()
                if "ACTIV" in estado_paso or posicion == "tramite_actual":
                    return "🟡", "Tu trámite está en proceso.\n"
        except Exception:
            pass

        # sino, por defecto rojo (recepcionado -> en cola)
        return "🔴", "Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro."

    if any(k in ef for k in ("ENVIAD", "EN PROCESO", "EN TRAMITE", "EN TRÁMITE")) or any(
        k in dp for k in ("ENVIAD", "EN PROCESO", "EN TRAMITE", "EN TRÁMITE")
    ):
        return "🟡", "Tu trámite está en proceso.\n"

    return "🟡", "Tu trámite está en proceso.\n"


def obtener_estado_real(historial: List[dict]) -> Tuple[dict, dict]:
    """
    Devuelve (fila_seleccionada, nodo_seleccionado)
    Estrategia (robusta):
    1) última fila con estado == 'RECIBIDO'
    2) última fila con estado_paso_detalle == 'ACTIVO'
    3) última con posicion == 'tramite_actual'
    4) última fila que contenga nodo_activo o nodo_previo
    5) última fila por fecha
    (Se mantiene esta prioridad pero la selección final de nodo se
     ajusta en _seleccionar_nodo_para_mostrar)
    """
    if not historial:
        return {}, {}

    recibidos = [h for h in historial if (h.get("estado") or "").strip().upper() == "RECIBIDO"]
    if recibidos:
        fila = sorted(recibidos, key=_obtener_fecha_fila, reverse=True)[0]
        nodo = fila.get("nodo_activo") or fila.get("nodo_previo") or {}
        return fila, nodo

    activos = [h for h in historial if (h.get("estado_paso_detalle") or "").strip().upper() == "ACTIVO"]
    if activos:
        fila = sorted(activos, key=_obtener_fecha_fila, reverse=True)[0]
        nodo = fila.get("nodo_activo") or fila.get("nodo_previo") or {}
        return fila, nodo

    actuales = [h for h in historial if (h.get("posicion") or "").strip().lower() == "tramite_actual"]
    if actuales:
        fila = sorted(actuales, key=_obtener_fecha_fila, reverse=True)[0]
        nodo = fila.get("nodo_activo") or fila.get("nodo_previo") or {}
        return fila, nodo

    con_nodo = [h for h in historial if h.get("nodo_activo") or h.get("nodo_previo")]
    if con_nodo:
        fila = sorted(con_nodo, key=_obtener_fecha_fila, reverse=True)[0]
        nodo = fila.get("nodo_activo") or fila.get("nodo_previo") or {}
        return fila, nodo

    fila = sorted(historial, key=_obtener_fecha_fila, reverse=True)[0]
    nodo = fila.get("nodo_activo") or fila.get("nodo_previo") or {}
    return fila, nodo


def _debe_mostrar_nodo_previo_por_por_recibir(estado_field: str, descripcion: str, nodo_real: dict, fila: dict) -> bool:
    """
    Detección más amplia de 'por recibirse' buscando en varios campos.
    """
    ef = (estado_field or "").upper()
    dp = (descripcion or "").upper()

    # construir string con campos del nodo_real
    node_str = ""
    if nodo_real:
        node_str = " ".join([str(nodo_real.get(k, "")).upper() for k in ("nombre_nodo", "nodo", "descripcion", "usuario")])

    # revisar fila completa
    fila_str = ""
    if fila and isinstance(fila, dict):
        fila_str = " ".join([str(fila.get(k, "")).upper() for k in ("estado", "estado_paso_detalle", "descripcion_proveido")])

    candidates = [ef, dp, node_str, fila_str]
    for c in candidates:
        if any(x in c for x in ("POR RECIB", "PORRECIB", "POR RECIBIR", "PORRECIBIR")):
            return True
    return False


def _seleccionar_nodo_para_mostrar(fila_real: dict, nodo_real: dict, historial: List[dict], estado_field: str, descripcion: str, semaforo_emoji: str) -> Tuple[dict, bool]:
    """
    Decide nodo a mostrar y si usar 'fecha actual' (True) o 'fecha anterior' (False).
    Devuelve (nodo_para_mostrar, usar_fecha_actual).

    Reglas clave implementadas (ajustada según tu pedido):
      - Si la fila tiene posicion == 'tramite_actual' y existe nodo_activo con estado ACTIVO o el estado de fila es RECIBIDO ->
        mostrar nodo_activo y usar fecha actual (asegura que se muestre el nodo_actual cuando esté en curso).
      - Si la fila tiene posicion == 'tramite_actual' y existe nodo_previo pero no se cumplen las condiciones anteriores -> mostrar nodo_previo.
      - Por recibir -> devolver nodo_previo si existe; usar_fecha_actual = False
      - Si nodo actual es asistente/apoyo y en historial existe plataforma anterior -> mostrar la plataforma (False)
      - Si semaforo == '🔴' -> usar_fecha_actual = True
      - Para '🟡' y casos por defecto -> usar_fecha_actual = False excepto el caso especial de "tramite_actual" (arriba)
    """
    nodo_a_mostrar = nodo_real or {}
    usar_fecha_actual = False

    posicion = (fila_real.get("posicion") or "").strip().lower() if fila_real else ""
    try:
        if fila_real and isinstance(fila_real, dict):
            prev = fila_real.get("nodo_previo") if isinstance(fila_real.get("nodo_previo"), dict) else None
            activo = fila_real.get("nodo_activo") if isinstance(fila_real.get("nodo_activo"), dict) else None

            # NUEVA LÓGICA: detectar si nodo_activo es plataforma finalizados u observados
            is_finalizados_plat, is_observados_plat = _nodo_es_plataforma_finalizados_o_observados(activo)

            # Si es OBSERVADOS PLATAFORMA -> mostrar siempre nodo_activo (no mostrar prev)
            if posicion == "tramite_actual" and activo and is_observados_plat:
                return activo, False

            # Si es FINALIZADOS PLATAFORMA y semáforo verde -> mostrar nodo_activo
            if posicion == "tramite_actual" and activo and is_finalizados_plat and semaforo_emoji == "🟢":
                return activo, False

            # Si estamos en "tramite_actual" y hay nodo_activo y la fila indica actividad (ACTIVO) o el estado es RECIBIDO -> mostrar nodo_activo y usar fecha actual
            estado_paso = (fila_real.get("estado_paso_detalle") or "").upper()
            estado_field_local = (estado_field or "").upper()
            if posicion == "tramite_actual" and activo and ("ACTIV" in estado_paso or "RECIB" in estado_field_local):
                return activo, True

            # REGLA por defecto: si posicion == 'tramite_actual' y existe prev -> mostrar prev
            if posicion == "tramite_actual" and prev:
                return prev, False

            # Si nodo_actual es administrativo (ASISTENTE/APOYO) y existe una plataforma anterior en el historial -> mostrar la plataforma previa (no la administrativa)
            nodo_nombre = (activo.get("nombre_nodo") or activo.get("nodo") or "").upper() if activo else ""
            if nodo_nombre and any(x in nodo_nombre for x in ADMIN_KEYWORDS) and historial:
                for h in reversed(historial):
                    cand = h.get("nodo_activo") or h.get("nodo_previo")
                    if cand:
                        cand_nombre = (cand.get("nombre_nodo") or cand.get("nodo") or "").upper()
                        if any(x in cand_nombre for x in PLATFORM_KEYWORDS):
                            return cand, False
    except Exception:
        pass

    # 1) Por recibir/por recibirse -> mostrar previo si existe (REGLA PRIORITARIA secundaria)
    try:
        if _debe_mostrar_nodo_previo_por_por_recibir(estado_field, descripcion, nodo_real or {}, fila_real or {}):
            prev = None
            if fila_real and isinstance(fila_real, dict):
                prev = fila_real.get("nodo_previo") or {}
            if not prev and historial:
                for h in reversed(historial):
                    cand = h.get("nodo_previo") or h.get("nodo_activo")
                    if cand and cand != nodo_real:
                        prev = cand
                        break
            if prev:
                return prev, False
    except Exception:
        pass

    # 2) Si nodo actual es administrativo y hay plataforma anterior -> mostrar la plataforma
    try:
        nodo_nombre = (nodo_real.get("nombre_nodo") or nodo_real.get("nodo") or "").upper() if nodo_real else ""
        if nodo_nombre and any(x in nodo_nombre for x in ADMIN_KEYWORDS) and historial:
            for h in reversed(historial):
                cand = h.get("nodo_activo") or h.get("nodo_previo")
                if cand:
                    cand_nombre = (cand.get("nombre_nodo") or cand.get("nodo") or "").upper()
                    if any(x in cand_nombre for x in PLATFORM_KEYWORDS):
                        return cand, False
    except Exception:
        pass

    # 3) flags por semáforo: rojo siempre usa fecha actual; amarillo usa fecha actual si estamos en 'tramite_actual'
    if semaforo_emoji == "🔴":
        usar_fecha_actual = True
    elif semaforo_emoji == "🟡" and posicion == "tramite_actual":
        usar_fecha_actual = True
    else:
        usar_fecha_actual = False

    return nodo_a_mostrar, usar_fecha_actual


def _obtener_fecha_display(fila_real: dict, historial: List[dict], usar_fecha_actual: bool) -> Optional[datetime]:
    if usar_fecha_actual and fila_real:
        for k in ("fecha_recepcion", "fecha_envio", "fecha_iso"):
            v = fila_real.get(k)
            dt = _parse_fecha_corta(v)
            if dt:
                return dt
    # si no pedimos fecha actual o no la encontramos, buscar en fila_real la última fecha válida
    if fila_real:
        for k in ("fecha_iso", "fecha_envio", "fecha_recepcion"):
            v = fila_real.get(k)
            dt = _parse_fecha_corta(v)
            if dt:
                return dt
    if historial:
        for h in reversed(historial):
            for k in ("fecha_iso", "fecha_recepcion", "fecha_envio"):
                v = h.get(k)
                dt = _parse_fecha_corta(v)
                if dt:
                    return dt
    return None


def _formatear_ubicacion_con_siglas(nodo: dict) -> str:
    """
    Construye string de ubicación incluyendo siglas cuando están disponibles:
    Ej: "PROCESADOR CATASTRAL de la UNIDAD DE REGISTRO Y SERVICIOS CATASTRALES (URSC)"
    o "PLATAFORMA INTEGRAL MIRAFLORES - (USAC)"
    """
    nombre_nodo = (nodo.get("nombre_nodo") or nodo.get("nodo") or "").strip()
    uo_desc = (nodo.get("uo_sigla_descripcion") or "").strip()
    uo = (nodo.get("uo_sigla") or "").strip()

    parts = []
    if nombre_nodo:
        parts.append(nombre_nodo)
    if uo_desc:
        parts.append(f"de la {uo_desc}")
    if uo:
        parts.append(f"({uo})")
    return " ".join(p for p in parts if p) or "(información de nodo no disponible)"


def _operador_del_estado(current_state: dict) -> str:
    """
    Intenta obtener el nombre del operador que 'lo tiene'.
    Maneja distintos nombres de campo según tu ejemplo.
    """
    if not current_state or not isinstance(current_state, dict):
        return ""
    # buscar en la fila actual
    for key in ("usuario_recepcion_nombre", "usuario_operador_nombre", "nombre_completo", "usuario"):
        v = current_state.get(key)
        if v:
            return v
    # si se pasó el dict que contiene nodo_activo/nodo_previo anidado
    nodo_activo = current_state.get("nodo_activo") if isinstance(current_state.get("nodo_activo"), dict) else None
    if nodo_activo:
        for key in ("usuario_recepcion_nombre", "usuario_operador_nombre", "nombre_completo", "usuario"):
            v = nodo_activo.get(key)
            if v:
                return v
    # también buscar en data_tramite.usuario.nombre_completo
    data_tramite = current_state.get("data_tramite") if isinstance(current_state.get("data_tramite"), dict) else None
    if data_tramite:
        usuario = data_tramite.get("usuario") if isinstance(data_tramite.get("usuario"), dict) else None
        if usuario:
            for key in ("nombre_completo", "usuario"):
                v = usuario.get(key)
                if v:
                    return v
    return ""


def _dias_desde_fecha(fecha_iso: str) -> int:
    if not fecha_iso:
        return 0
    try:
        fecha_inicial = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00"))
        ahora = datetime.now(timezone.utc)
        delta = ahora.date() - fecha_inicial.date()
        return max(delta.days, 0)
    except Exception:
        try:
            fecha_inicial = _parse_fecha_corta(fecha_iso)
            if fecha_inicial:
                ahora = datetime.now(timezone.utc)
                delta = ahora.date() - fecha_inicial.date()
                return max(delta.days, 0)
        except Exception:
            pass
    return 0


# ---------------------------------------------------------------------------
# Helpers implementando exactamente tu flujo (según descripción)
# ---------------------------------------------------------------------------

def _nombre_nodo_upper(nodo: Optional[dict]) -> str:
    if not nodo or not isinstance(nodo, dict):
        return ""
    return ((nodo.get("nombre_nodo") or nodo.get("nodo") or "")).upper()


def _es_plataforma_nodo(nodo: Optional[dict]) -> bool:
    name = _nombre_nodo_upper(nodo)
    if not name:
        return False
    return any(k in name for k in ("PLATAFORMA INTEGRAL", "MIRAFLORES", "CAMACHO", "SUR"))


def _es_admin_nodo(nodo: Optional[dict]) -> bool:
    name = _nombre_nodo_upper(nodo)
    if not name:
        return False
    return any(k in name for k in ("ASISTENTE ADMINISTRATIVO", "APOYO ADMINISTRATIVO", "ASISTENTE", "APOYO"))


def _buscar_antecedente1_2(fila_real: dict, historial: List[dict]) -> Tuple[Optional[dict], Optional[dict]]:
    """
    Intenta obtener antecedente1 y antecedente2 con preferencia:
    - antecedente1: fila_real.nodo_previo
    - antecedente2: antecedente1.nodo_previo (si existe)
    Si no existen, busca en historial (reversed) las últimas entradas con nodo_previo/nodo_activo.
    """
    a1 = None
    a2 = None
    try:
        if fila_real and isinstance(fila_real, dict):
            a1 = fila_real.get("nodo_previo") if isinstance(fila_real.get("nodo_previo"), dict) else None
            if a1 and isinstance(a1, dict):
                a2 = a1.get("nodo_previo") if isinstance(a1.get("nodo_previo"), dict) else None
    except Exception:
        pass

    if not a1 and historial:
        for h in reversed(historial):
            cand = h.get("nodo_previo") or h.get("nodo_activo")
            if cand and isinstance(cand, dict):
                a1 = cand
                break
    if a1 and not a2 and historial:
        # buscar la instancia anterior a a1 en historial
        found = False
        for h in reversed(historial):
            cand = h.get("nodo_activo") or h.get("nodo_previo")
            if cand and isinstance(cand, dict):
                if found:
                    a2 = cand
                    break
                # determinar si este cand corresponde a a1 (por nombre)
                name_cand = _nombre_nodo_upper(cand)
                name_a1 = _nombre_nodo_upper(a1)
                if name_cand == name_a1:
                    found = True
    return a1, a2


def _aplicar_reglas_de_flujo(nodo_actual: Optional[dict],
                             fila_real: dict,
                             historial: List[dict],
                             estado_field: str) -> Tuple[Optional[str], Optional[bool], bool, Optional[str]]:
    """
    Aplica la lógica que me explicaste y devuelve:
    (override_semaforo_emoji, override_usar_fecha_actual (True/False/None), include_assignment_msgs, override_text_estado)
    Si override_semaforo_emoji es None -> no override (usar lo calculado antes).
    include_assignment_msgs -> si True agregar los textos de "Próximo paso..." / "Comentarios adicionales..."
    override_text_estado -> texto corto para mostrar junto al emoji (opcional).
    """
    estado_up = (estado_field or "").upper()
    nodo_name = _nombre_nodo_upper(nodo_actual)
    a1, a2 = _buscar_antecedente1_2(fila_real or {}, historial or [])

    # helper checks
    is_nodo_plat = _es_plataforma_nodo(nodo_actual)
    is_nodo_admin = _es_admin_nodo(nodo_actual)
    is_a1_plat = _es_plataforma_nodo(a1)
    is_a1_admin = _es_admin_nodo(a1)
    is_a2_plat = _es_plataforma_nodo(a2)

    # Detectar si nodo_actual es FINALIZADOS/OBSERVADOS de plataforma
    is_finalizados_plat, is_observados_plat = _nodo_es_plataforma_finalizados_o_observados(nodo_actual)

    # --- NUEVA PRIORIDAD: manejar FINALIZADOS/OBSERVADOS primero (según tu pedido) ---
    if is_finalizados_plat:
        # Si es FINALIZADOS PLATAFORMA:
        if "RECIB" in estado_up:
            return "🟢", True, False, "Tu trámite ha finalizado."
        if "CERR" in estado_up:
            return "⚪", True, False, "Tu trámite está cerrado."
        # si no es RECIB ni CERR -> amarillo y mostrar fecha anterior / ubicación
        return "🟡", False, False, "Tu trámite está en proceso.\n"

    if is_observados_plat:
        # Si es OBSERVADOS PLATAFORMA:
        if "RECIB" in estado_up:
            # RECIBIDO + OBSERVADOS -> verde y texto "finalizado"
            return "🟢", True, False, "Tu trámite ha finalizado."
        if "CERR" in estado_up:
            return "⚪", True, False, "Tu trámite está cerrado."
        # por defecto observado -> amarillo (fecha anterior)
        return "🟢", False, False, "Tu trámite ha finalizado."

    # 1) Si el primer nodo es una de las plataformas/administrativos listados:
    if nodo_actual and (is_nodo_plat or is_nodo_admin):
        # Si es plataforma directamente:
        if is_nodo_plat:
            include_assignment = True
            if "RECIB" in estado_up:
                return "🔴", True, include_assignment, "Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro."
            else:
                return "🔴", False, include_assignment, "Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro."
        # si es admin (ej: ASISTENTE / APOYO)
        if is_nodo_admin:
            # mirar antecedente1
            if a1 and is_a1_plat:
                include_assignment = True
                if "RECIB" in estado_up:
                    return "🔴", True, include_assignment, "Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro."
                else:
                    return "🔴", False, include_assignment, "Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro."
            # si a1 no es plataforma, pero a1 es admin y a2 es plataforma -> amarillo
            if a1 and is_a1_admin and a2 and is_a2_plat:
                include_assignment = False
                if "RECIB" in estado_up:
                    return "🟡", True, include_assignment, "Tu trámite está en proceso.\n"
                else:
                    return "🟡", False, include_assignment, "Tu trámite está en proceso.\n"
            # si no se cumple ninguna cadena -> fallback a reglas por estado (None)
            return None, None, False, None

    # 2) Si la bandeja actual no es finalizados/observados: revisar antecedentes
    if (a1 and (is_a1_admin or is_a1_plat)) and a2 and is_a2_plat:
        # según tu texto: si estado RECIBIDO -> amarillo actual; si no RECIBIDO -> amarillo anterior
        if "RECIB" in estado_up:
            return "🟡", True, False, "Tu trámite está en proceso.\n"
        else:
            return "🟡", False, False, "Tu trámite está en proceso.\n"

    # 3) Si antecedente1 es plataforma pero nodo actual no es plataforma (pudo ser admin u otro):
    if a1 and is_a1_plat:
        # según tu descripción, se trata como rojo (asignación)
        include_assignment = True
        if "RECIB" in estado_up:
            return "🔴", True, include_assignment, "Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro."
        else:
            return "🔴", False, include_assignment, "Tu trámite fue recepcionado y sera asignado a un técnico en la unidad de catastro."

    # 4) Regla por defecto si no entró en ninguna rama:
    #    revisar estado:
    if "RECIB" in estado_up:
        return "🟡", True, False, "Tu trámite está en proceso.\n"
    if "CERR" in estado_up:
        return "⚪", True, False, "Tu trámite está cerrado."
    # si otro estado -> amarillo anterior
    return "🟡", False, False, "Tu trámite está en proceso.\n"


# ---------------------------------------------------------------------------
# flujo principal (mantengo tu interfaz)
async def flujo_opcion_a(
    texto_real: str,
    numero: str,
    user_state: dict,
    name: str = "",
    id_boton: str = "",
) -> List[Dict[str, Any]]:

    dataList: List[Dict[str, Any]] = []
    estado = (user_state or {}).get("estado", "")
    t = (texto_real or "").strip().lower()

    if t in {
        "catastro",
        "catastro-menu",
        "catastro:menu",
        "volver al menu catastral",
        "volver al menú catastral",
    }:
        await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
        body = "Selecciona una de las opciones que tenemos en catastro:"
        payload_lista = await crear_payload_lista(
            numero=numero,
            cuerpo=_fit_whatsapp_body(body),
            opciones=obtener_opciones_catastro(),
            header_text="",
            footer_text="",
            button_text="Inf. catastral",
        )
        dataList.append(payload_lista)
        return dataList

    if t in CANCEL_KEYWORDS:
        await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
        body = (
            "😌 Está bien, no hay problema.\n"
            "🔔 Puedes hacerlo en cualquier momento desde este chat.\n"
            "¿Puedo ayudarte con algo más?\n"
            "Selecciona una de las opciones que tenemos en catastro:"
        )
        payload_lista = await crear_payload_lista(
            numero=numero,
            cuerpo=_fit_whatsapp_body(body),
            opciones=obtener_opciones_catastro(),
            header_text="",
            footer_text="AMI Catastro",
            button_text="Inf. catastral",
        )
        dataList.append(payload_lista)
        return dataList

    if estado == "esperando-opcion" and t == "catastro-a":
        await set_estado_usuario(numero, {"contexto": "catastro", "estado": "catastro-a-a"})
        mensaje_bienvenida = (
            f"¡Hola 😊 {name} 🌟, vamos a realizar el seguimiento de tu trámite catastral!\n\n"
            f"Por favor, ingresa el número de trámite:"
        )
        payload = await crear_payload_button(numero, mensaje_bienvenida, "", "salir", "Cancelar")
        dataList.append(payload)
        return dataList

    if estado == "catastro-a-a":
        if _valido(texto_real):
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "catastro-busca-tramite", "numero-tramite": texto_real})
            payload = await crear_payload_button(numero, "🔐 Por favor ingresa la *contraseña del trámite* (ejemplo: 12345ABC):", "", "salir", "Cancelar")
        else:
            payload = await crear_payload_button(numero, "🚫 Número inválido. Ingresa mínimo 3 dígitos o letras:", "", "salir", "Cancelar")
        dataList.append(payload)
        return dataList

    if estado == "catastro-busca-tramite":
        spinner = await crear_payload_texto(numero, "⏳ Estamos verificando tus datos...")
        dataList.append(spinner)

        if _valido(texto_real):
            numero_tramite = (user_state or {}).get("numero-tramite")
            await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
            resultado = await _procesar_tramite(numero_tramite, texto_real)
            body = _fit_whatsapp_body(resultado.get("mensaje", ""))
            payload_lista = await crear_payload_lista(numero=numero, cuerpo=body, opciones=opciones_postconsulta(), header_text="", footer_text="", button_text="Ver opciones")
            dataList.append(payload_lista)
        else:
            payload = await crear_payload_button(numero, "🚫 Contraseña inválida. Intenta nuevamente:", "", "salir", "Cancelar")
            dataList.append(payload)

        return dataList

    return dataList


# ---------------------------------------------------------------------------
async def _procesar_tramite(numero_tramite: str, contra_tramite: str) -> Dict[str, Any]:
    """
    Devuelve {"mensaje": str}
    Reglas implementadas: selección de nodo previo en 'por recibir', semáforos, siglas, mapa SOLO si verde.
    Ajustes solicitados:
      - Cuando el estado es ENTRANTE -> mostrar ROJO, mostrar nodo_previo y fecha anterior, incluir próximo paso y comentarios.
      - Cuando el estado es ANULADO -> mostrar mensaje simple: "El trámite fue anulado" con ROJO y fecha.
      - Se integra la lógica completa de flujo que me proporcionaste (primer nodo, antecedentes, finalizados/observados).
      - *Comportamiento adicional:* cuando el estado sea CERRADO, se muestra **solo** el bloque reducido (estado blanco) con las líneas solicitadas.
    """
    try:
        respuesta = await consulta_tramite({"numero": numero_tramite, "contra": contra_tramite})

        if not respuesta or not respuesta.get("estado"):
            return {"mensaje": "❌ No se logró identificar el trámite. Verifica si el número o contraseña son correctos."}

        data = respuesta["data"]["data_principal"] if respuesta.get("data") else {}
        historial = respuesta["data"].get("historial", []) if respuesta.get("data") else []

        # nombre: preferir capitalización normal si ya viene con minúsculas, sino Title()
        nombre_raw = data.get("remitente") or "Usuario"
        nombre = nombre_raw if any(c.islower() for c in nombre_raw) else nombre_raw.title()

        asunto = _limpiar_asunto(data.get("asunto"))

        fila_real, nodo_real = obtener_estado_real(historial)
        if not nodo_real and fila_real:
            nodo_real = fila_real.get("nodo_activo") or fila_real.get("nodo_previo") or {}

        # estado_field: preferir el estado que venga en la fila (más cercano a la realidad)
        estado_field = (fila_real.get("estado") if fila_real else "") or (data.get("estado") or "")
        descripcion_proveido_ultimo = (fila_real.get("descripcion_proveido") or "") if fila_real else ""
        nodo_nombre_for_semaforo = (nodo_real.get("nombre_nodo") or nodo_real.get("nodo") or "") if nodo_real else ""

        # PASAMOS fila_real a la función de semáforo para manejar casos como RECIBIDO+ACTIVO -> 🟡
        semaforo_emoji, texto_estado = determinar_semaforo_texto(estado_field, descripcion_proveido_ultimo, nodo_nombre_for_semaforo, fila_real)

        # Seleccionar nodo a mostrar inicialmente
        nodo_para_mostrar, usar_fecha_actual = _seleccionar_nodo_para_mostrar(
            fila_real=fila_real or {},
            nodo_real=nodo_real or {},
            historial=historial or [],
            estado_field=estado_field,
            descripcion=descripcion_proveido_ultimo,
            semaforo_emoji=semaforo_emoji,
        )

        # === APLICAR REGLAS DEL FLUJO (OVERRIDES) ===
        override_semaforo, override_fecha_flag, include_assignment_msgs, override_text_estado = _aplicar_reglas_de_flujo(
            nodo_actual=nodo_para_mostrar or nodo_real,
            fila_real=fila_real or {},
            historial=historial or [],
            estado_field=estado_field or "",
        )

        if override_semaforo:
            semaforo_emoji = override_semaforo
        if override_text_estado:
            texto_estado = override_text_estado
        if override_fecha_flag is not None:
            usar_fecha_actual = override_fecha_flag

        # === REGLA: ANULADO -> mostrar mensaje simple, rojo y fecha ===
        if "ANUL" in (estado_field or "").upper() or "ANUL" in (descripcion_proveido_ultimo or "").upper():
            semaforo_emoji = "🔴"
            fecha_display_dt = _obtener_fecha_display(fila_real or {}, historial or [], False)
            fecha_mod_literal = "No disponible"
            if fecha_display_dt:
                try:
                    fecha_mod_literal = format_date(fecha_display_dt.date(), format="full", locale="es")
                except Exception:
                    fecha_mod_literal = fecha_display_dt.isoformat()

            partes = []
            partes.append(f"👋 ¡Hola, {nombre}!")
            partes.append(f"📄 Tu trámite N° {numero_tramite}")
            partes.append(f"{semaforo_emoji} El trámite fue anulado.")
            partes.append(f"📆 Última fecha de actualización: {fecha_mod_literal}.")
            mensaje = "\n".join(p for p in partes if p)
            return {"mensaje": _fit_whatsapp_body(mensaje, limit=1024)}

        # === REGLA ESPECIAL: CERRADO -> mostrar SOLO bloque 'blanco' reducido y retornar (petición del usuario) ===
        if "CERR" in (estado_field or "").upper():
            # Forzar emoji y texto correctos para CERRADO (evitamos overrides previos)
            semaforo_emoji = "⚪"
            texto_estado = "Tu trámite está cerrado."

            # usar fecha actual para CERRADO (según tu especificación)
            fecha_display_dt = _obtener_fecha_display(fila_real or {}, historial or [], True)
            fecha_ingreso_literal = "No disponible"
            fecha_mod_literal = "No disponible"
            # fecha de ingreso: preferir fecha de creación del trámite si existe en data
            try:
                if data.get("fecha_creacion"):
                    fecha_ingreso_dt = datetime.fromisoformat(data.get("fecha_creacion").replace("Z", "+00:00"))
                    fecha_ingreso_literal = format_date(fecha_ingreso_dt.date(), format="full", locale="es")
            except Exception:
                fecha_ingreso_literal = "No disponible"

            if fecha_display_dt:
                try:
                    fecha_mod_literal = format_date(fecha_display_dt.date(), format="full", locale="es")
                except Exception:
                    fecha_mod_literal = fecha_display_dt.isoformat()

            partes = []
            partes.append(f"👋 ¡Hola, {nombre}!")
            partes.append(f"📄 Tu trámite N° {numero_tramite}")
            partes.append(f"🔎 Asunto: {asunto}")
            partes.append(f"{semaforo_emoji} {texto_estado}")  # forzado a "Tu trámite está cerrado."
            partes.append("-------------------------")
            partes.append(f"📆 El trámite ingreso: {fecha_ingreso_literal}.")
            partes.append(f"📆️ Última fecha de actualización: {fecha_mod_literal}.")
            mensaje = "\n".join(p for p in partes if p)
            return {"mensaje": _fit_whatsapp_body(mensaje, limit=1024)}

        # === REGLA: ENTRANTE -> mostrar ROJO, nodo_previo y fecha anterior, con texto extra ===
        if "ENTRANT" in (estado_field or "").upper() or (fila_real and ((fila_real.get("estado") or "").upper() == "ENTRANTE")):
            semaforo_emoji = "🟡"
            texto_estado = "Tu trámite está en proceso.\n"
            # preferir nodo_previo
            prev = (fila_real.get("nodo_previo") if fila_real and isinstance(fila_real.get("nodo_previo"), dict) else None)
            if prev:
                nodo_para_mostrar = prev
                usar_fecha_actual = False
            else:
                # si no hay previo pero el nodo actual es administrativo y en historial hay una plataforma, preferirla
                nodo_nombre = (nodo_para_mostrar.get("nombre_nodo") or nodo_para_mostrar.get("nodo") or "").upper() if nodo_para_mostrar else ""
                if nodo_nombre and any(x in nodo_nombre for x in ADMIN_KEYWORDS) and historial:
                    for h in reversed(historial):
                        cand = h.get("nodo_activo") or h.get("nodo_previo")
                        if cand:
                            cand_nombre = (cand.get("nombre_nodo") or cand.get("nodo") or "").upper()
                            if any(x in cand_nombre for x in PLATFORM_KEYWORDS):
                                nodo_para_mostrar = cand
                                usar_fecha_actual = False
                                break

        # === FIN de reglas especiales ===

        fecha_literal = "No disponible"
        try:
            if data.get("fecha_creacion"):
                fecha_ingreso = datetime.fromisoformat(data.get("fecha_creacion").replace("Z", "+00:00"))
                fecha_literal = format_date(fecha_ingreso.date(), format="full", locale="es")
        except Exception:
            fecha_literal = "No disponible"

        fecha_display_dt = _obtener_fecha_display(fila_real or {}, historial or [], usar_fecha_actual)
        fecha_mod_literal = "No disponible"
        if fecha_display_dt:
            try:
                fecha_mod_literal = format_date(fecha_display_dt.date(), format="full", locale="es")
            except Exception:
                fecha_mod_literal = fecha_display_dt.isoformat()

        # construir link único al historial
        posible_id = ""
        if isinstance(data, dict):
            for k in ("nro_tramite_sigla", "nro_tramite", "nro_cite"):
                v = data.get(k)
                if v:
                    posible_id = str(v).strip()
                    break
        if not posible_id and numero_tramite:
            posible_id = str(numero_tramite).strip()

        link_base = f"https://{OFFICIAL_HOST}{OFFICIAL_PATH}"
        link_historial = link_base
        if posible_id:
            link_historial = f"{link_base}?id={quote_plus(posible_id)}"

        # Construcción mensaje completo cuando no cerrado
        recibido_por = _operador_del_estado(nodo_para_mostrar) or _operador_del_estado(fila_real)
        ubicacion_text = _formatear_ubicacion_con_siglas(nodo_para_mostrar)

        partes: List[str] = []
        partes.append(f"👋 ¡Hola, {nombre}!")
        partes.append(f"📄 Tu trámite N° {numero_tramite}")
        partes.append(f"🔎 Asunto: {asunto}")
        # semáforo y posible separador según color:
        partes.append(f"{semaforo_emoji} {texto_estado}")
        incluir_separadores = semaforo_emoji == "🟢"  # Solo mostramos las líneas '-----------------' para verde
        if incluir_separadores:
            partes.append("")

        # Mostrar fechas y ubicación
        # Si el estado fue ENTRANTE y forzamos usar nodo_previo, queremos que la fecha mostrada sea la anterior (usar_fecha_actual False)
        partes.append(f"📆 El trámite ingreso: {fecha_literal}.")
        partes.append(f"📆️ Última fecha de actualización: {fecha_mod_literal}.")

        dias = _dias_desde_fecha(data.get("fecha_creacion") or "")
        # Diferente texto de "días" para verde vs otros
        if semaforo_emoji == "🟢":
            partes.append(f"⏱️ Han pasado: {dias} días calendario hasta la fecha de finalización de tu trámite.")
        else:
            partes.append(f"⏱️ Han pasado: {dias} días")

        partes.append(f"📍 El trámite se encuentra en: {ubicacion_text}.")

        if recibido_por:
            partes.append(f"✅ Lo tiene recibido: {recibido_por}")

        # INSTRUCCIONES y MAPA: comportamiento especial para VERDE (plataformas finales)
        if semaforo_emoji == "🟢":
            # Detectar plataforma en nodo_para_mostrar (prioridad) o en nodo_activo/fila
            nodo_upper = ((nodo_para_mostrar.get("nombre_nodo") or nodo_para_mostrar.get("nodo") or "")).upper()
            # fallback: revisar fila_real.nodo_activo
            if not nodo_upper and fila_real and isinstance(fila_real, dict):
                nodo_activo = fila_real.get("nodo_activo") or {}
                nodo_upper = ((nodo_activo.get("nombre_nodo") or nodo_activo.get("nodo") or "")).upper()

            platform_key = None
            if "CAMACHO" in nodo_upper:
                platform_key = "CAMACHO"
            elif "MIRAFLORES" in nodo_upper:
                platform_key = "MIRAFLORES"
            elif "SUR" in nodo_upper:
                platform_key = "SUR"

            # instrucciones preferidas (prioridad: instrucción del nodo o data -> plataforma específica -> default)
            instrucciones = (
                (nodo_para_mostrar.get("instrucciones") if isinstance(nodo_para_mostrar, dict) else None)
                or data.get("instrucciones")
                or (nodo_para_mostrar.get("observacion") if isinstance(nodo_para_mostrar, dict) else None)
                or descripcion_proveido_ultimo
                or ""
            )

            if platform_key and MAPS_FOR_PLATFORM.get(platform_key):
                plat = MAPS_FOR_PLATFORM[platform_key]
                # si no hay instrucciones específicas en data/nodo usamos la del mapa/plataforma
                if not instrucciones.strip():
                    instrucciones = plat["instrucciones"]
                # agregar instrucciones
                if instrucciones and instrucciones.strip():
                    partes.append(instrucciones)
                # agregar link de la plataforma (maps)
                partes.append(f"Como llegar: {plat['link']}")
            else:
                # fallback normal: usar instrucciones del nodo/data o default y buscar link en historial
                if instrucciones and instrucciones.strip():
                    partes.append(instrucciones)
                else:
                    partes.append(DEFAULT_INSTRUCCIONES)
                map_link = _buscar_map_link(historial, nodo_para_mostrar or {}, data) or DEFAULT_MAP_LINK
                if map_link:
                    partes.append(f"Como llegar: {map_link}")

        # Separador e "Información útil" según color
        if incluir_separadores:
            partes.append("")
            partes.append("✅ Información útil:")
        else:
            # NO mostrar la raya de separación; agregar un salto en blanco antes del encabezado
            partes.append("")  # línea en blanco
            partes.append("Información útil:")

        partes.append("1. Atención de 08:15hrs. a 17:30hrs (continuo).")
        partes.append(
            "2. El titular debe presentarse con su carnet de identidad; si lo recoge un apoderado, presentar poder notarial y su carnet."
         
        )
        partes.append(
            "Prevenir: Si en 90 días no recoge su trámite, será archivado. Para retirarlo, deberá solicitar su desarchivo mediante una nota."
        )

        # Un único link al historial (al final)
        partes.append(f"Historial del trámite: {link_historial}")

        mensaje = "\n".join(p for p in partes if p is not None)
        mensaje = _fit_whatsapp_body(mensaje, limit=1024)
        return {"mensaje": mensaje}

    except Exception as error:
        print(f"❌ Error al consultar el trámite: {error}")
        return {"mensaje": "❌ Ocurrió un error interno al consultar el trámite. Intenta nuevamente más tarde."}
