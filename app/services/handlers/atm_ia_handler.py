# app/services/handlers/atm_inteligencia_handler.py
"""
ATM Inteligencia Handler — Versión Profesional (mejor formato)
- GPT-3.5 solo para razonamiento/normalización de la consulta (opcional).
- Respuestas extraídas únicamente desde ATM_KNOWLEDGE (importado).
- Soporta texto y mensajes de voz (transcripción si OPENAI_AUDIO_KEY disponible).
- Soporta respuestas múltiples y búsqueda por exactitud, similitud y semántica simple.
- Formato de salida mejorado: negrillas, emojis, estructura clara y cierre.
"""

import os
import re
import logging
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from collections import defaultdict

# OpenAI SDK (opcional)
try:
    import openai
except Exception:
    openai = None

# Importa funciones de base de datos y el corpus
from app.database.database import get_estado_usuario, set_estado_usuario, registrar_historial
from app.services.openAI.atm_knowledge import ATM_KNOWLEDGE  # texto oficial (string)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_AUDIO_KEY = os.getenv("OPENAI_AUDIO_KEY", OPENAI_API_KEY)

# Ajustes de comportamiento (ajusta según precisión/recall deseada)
SHOW_SEPARATORS = False                   # formato de salida con separadores visuales
MIN_SIMILARITY_FOR_DIRECT_ANSWER = 0.72   # similitud basada en SequenceMatcher
SEMANTIC_SCORE_THRESHOLD = 1.6            # umbral compuesto para aceptar resultado semántico
MULTI_ANSWER_ENABLED = True               # si True devuelve varias respuestas si hay coincidencias fuertes
MULTI_ANSWER_TOP_K = 3                    # máximo respuestas a devolver en modo múltiple
CACHE_TTL_SECONDS = 30                    # cache corto para consultas repetidas

SEP = "\n━━━━━━━━━━━━━━━━━━━━━━\n"
EOS = " 🔚"
CIERRE_ESTANDAR = f"\n\n*PARA VOLVER ESCRIBA: SALIR*  •  *FORMULE OTRA PREGUNTA RELACIONADA.*{EOS}"

# Mensajes estándar (personalizables)
MSG_NO_COVERAGE = (
    "❌ *Lo siento.* No encontré información precisa para su consulta.\n\n"
    "➡️ Intente reformular la pregunta con más detalles o escriba *SALIR* para volver al menú."
)
MSG_NOT_UNDERSTOOD = (
    "❓ *No entendí su mensaje.* Por favor, reformúlelo o escriba *SALIR* para volver al menú."
)
MSG_ASK_PROMPT = (
    "✅ *Entendido.* Por favor escriba su pregunta y le responderé con la información disponible.\n\n"
    "➡️ Escriba *SALIR* para volver al menú principal."
)

GREETINGS = {"hola", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "inicio", "menu"}
EXIT_WORDS = {"salir", "/salir", "exit"}

EMOJI_MAP = {
    "pago": "💳",
    "horario": "🕒",
    "oficina": "📍",
    "contacto": "📲",
    "ley": "📜",
    "default": "ℹ️",
}

# Encabezados/variantes frecuentes para extracción por sección
HEADING_VARIANTS = {
    "¿Qué es?": ["¿Qué es?", "Qué es?", "Que es?"],
    "Beneficio principal:": ["Beneficio principal:", "Beneficio principal"],
    "Vigencia:": ["Vigencia:", "Vigencia"],
    "Alcance:": ["Alcance:", "Alcance"],
    "¿Puedo pagar por internet?": ["¿Puedo pagar por internet?", "Puedo pagar por internet", "pagar por internet"],
    "Más información": ["Más información", "Mas información", "Más información:"],
}

# ---------------------------
# UTILIDADES DE TEXTO
# ---------------------------
def _clean(text: Optional[str]) -> str:
    t = (text or "").strip()
    t = re.sub(r"\r\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[\u2500-\u257F]{3,}", "", t)
    return t.strip()

def _normalize_input(s: str) -> str:
    t = (s or "").lower()
    t = re.sub(r"[^0-9a-záéíóúñüç\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def is_gibberish(s: str) -> bool:
    if not s or not s.strip():
        return False
    s = s.strip()
    if len(s) < 3:
        return True
    letters = sum(1 for ch in s if ch.isalpha() or ch in "áéíóúñÁÉÍÓÚÑ")
    total = len(s)
    ratio = letters / total if total > 0 else 0
    if ratio < 0.40:
        return True
    words = s.split()
    if len(words) == 1 and not re.search(r"[aeiouáéíóú]", s, re.I):
        return True
    return False

# ---------------------------
# PARSEO Y SEGMENTACIÓN DEL CORPUS
# ---------------------------
def split_blocks_by_separator(full_text: str) -> List[str]:
    if not full_text:
        return []
    sep_exact = "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    if sep_exact in full_text:
        parts = [p.strip() for p in full_text.split(sep_exact) if p and p.strip()]
    else:
        parts = [p.strip() for p in re.split(r"\n{2,}", full_text) if p and p.strip()]
    parts = [_clean(p) for p in parts]
    return parts

def parse_qa_pairs(full_text: str) -> List[Dict[str, str]]:
    qa_list: List[Dict[str, str]] = []
    if not full_text:
        return qa_list
    pattern = re.compile(r"(¿[^\?\n]+\?)\s*\n([\s\S]*?)(?=(?:\n¿[^\?\n]+\?)|\Z)", re.M)
    matches = pattern.findall(full_text)
    for q, a in matches:
        question = _clean(q)
        answer = _clean(a)
        if question and answer:
            qa_list.append({"question": question, "answer": answer})
    if not qa_list:
        blocks = split_blocks_by_separator(full_text)
        for b in blocks:
            lines = [l.strip() for l in b.splitlines() if l.strip()]
            if not lines:
                continue
            if lines[0].endswith("?") or lines[0].startswith("¿"):
                q = lines[0]
                a = "\n".join(lines[1:]) if len(lines) > 1 else ""
                if q and a:
                    qa_list.append({"question": q, "answer": a})
            else:
                q = lines[0]
                a = "\n".join(lines[1:]) if len(lines) > 1 else ""
                if q and a:
                    qa_list.append({"question": q, "answer": a})
    return qa_list

def parse_offices_and_contacts(full_text: str) -> Dict[str, str]:
    res: Dict[str, str] = {}
    offices = re.findall(r"(OFICINA(?: CENTRAL| \d+)?\s*\n(?:.*?)(?=\n{2,}|$))", full_text, re.I | re.S)
    if offices:
        res["Oficinas"] = _clean("\n\n".join(offices))
    horarios = re.search(r"Horario[s]? de atención\s*\n([\s\S]*?)(?=\n{2,}|$)", full_text, re.I)
    if horarios:
        res["Horarios"] = _clean(horarios.group(0))
    contacto = re.search(r"(Consultas en línea[\s\S]*?(?:TikTok oficial[\s\S]*?)?)", full_text, re.I)
    if contacto:
        res["Contacto"] = _clean(contacto.group(1))
    if not res:
        res["Información"] = _clean(full_text)
    return res

# ---------------------------
# MÉTRICAS / BÚSQUEDA
# ---------------------------
def token_overlap_score(a: str, b: str) -> int:
    atoks = set(_normalize_input(a).split())
    btoks = set(_normalize_input(b).split())
    return len(atoks & btoks)

def sequence_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    try:
        return SequenceMatcher(None, a, b).ratio()
    except Exception:
        return 0.0

def semantic_search(prompt: str, qa_pairs: List[Dict[str, str]], top_n: int = 5) -> List[Tuple[Dict[str, str], float]]:
    scores: List[Tuple[Dict[str, str], float]] = []
    pnorm = _normalize_input(prompt)
    for qa in qa_pairs:
        q = qa.get("question", "")
        a = qa.get("answer", "")
        qnorm = _normalize_input(q)
        anorm = _normalize_input(a)
        overlap = token_overlap_score(pnorm, qnorm)
        sim_q = sequence_similarity(pnorm, qnorm)
        sim_a = sequence_similarity(pnorm, anorm)
        score = overlap * 1.5 + max(sim_q, sim_a) * 5.0
        scores.append((qa, float(score)))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]

# ---------------------------
# FORMATEO DE RESPUESTAS (mejorado)
# ---------------------------
def _stylize_question(q: str) -> str:
    """Devuelve la pregunta en formato destacado (emoji + negrita)."""
    q_clean = q.strip()
    return f"🔎 *{q_clean}*"

def _format_block(title: str, body: str, emoji: str = "") -> str:
    """Formatea un bloque: título (o pregunta) y cuerpo con cierre estándar."""
    title_line = title.strip() if title else ""
    body_clean = _clean(body)
    header = f"{emoji} " if emoji else ""
    if title_line:
        title_fmt = f"{header}*{title_line}*"
    else:
        title_fmt = header
    # respuesta: título en negrita, cuerpo en texto normal, cierre con instrucciones
    if SHOW_SEPARATORS:
        return f"{SEP}{title_fmt}\n\n{body_clean}\n{SEP}{CIERRE_ESTANDAR}"
    return f"{title_fmt}\n\n{body_clean}\n{CIERRE_ESTANDAR}"

def format_multi_answers(matches: List[Tuple[Dict[str,str], float]]) -> str:
    """
    Recibe lista de (qa, score) y formatea en un solo mensaje enumerado,
    con preguntas en negrita y respuestas legibles.
    """
    if not matches:
        return ""
    lines = []
    top = matches[:MULTI_ANSWER_TOP_K]
    for i, (qa, score) in enumerate(top, start=1):
        q = qa.get("question", "").strip()
        a = _clean(qa.get("answer", ""))
        lines.append(f"{i}. 🔹 *{q}*\n{a}")
    body = "\n\n".join(lines).strip()
    return f"*RESPUESTAS ENCONTRADAS*\n\n{body}\n{CIERRE_ESTANDAR}"

# ---------------------------
# RAZONAMIENTO CON GPT (normalizador)
# ---------------------------
async def call_gpt_normalizer(user_prompt: str, max_tokens: int = 200) -> Optional[Dict[str, Any]]:
    if openai is None or not OPENAI_API_KEY:
        return None
    try:
        openai.api_key = OPENAI_API_KEY
        system_msg = (
            "Eres un asistente cuya tarea ÚNICA es normalizar y sintetizar la intención "
            "de una pregunta en lenguaje natural para que un buscador interno recupere información "
            "de un documento. Devuelve solo un JSON con 'clarified' y 'keywords'."
        )
        user_msg = f"Usuario preguntó: '''{user_prompt}'''\n\nDevuelve JSON {{'clarified': '...', 'keywords': 'kw1, kw2'}}."
        loop = asyncio.get_event_loop()
        def _call():
            return openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=max_tokens,
                temperature=0.0,
                top_p=1.0,
            )
        resp = await loop.run_in_executor(None, _call)
        content = resp.choices[0].message.content.strip()
        m = re.search(r"(\{[\s\S]*\})", content)
        if m:
            import json
            try:
                return json.loads(m.group(1))
            except Exception:
                try:
                    return eval(m.group(1))
                except Exception:
                    return {"clarified": content, "keywords": ""}
        else:
            return {"clarified": content, "keywords": ""}
    except Exception as e:
        logger.exception("Error en call_gpt_normalizer: %s", e)
        return None

# ---------------------------
# TRANSCRIPCIÓN DE AUDIO (soporte voz -> texto)
# ---------------------------
async def transcribe_audio_bytes(audio_bytes: bytes, filename_hint: str = "audio.ogg") -> Optional[str]:
    if openai is None or not OPENAI_AUDIO_KEY:
        logger.debug("Transcripción no disponible (OpenAI no configurado).")
        return None
    try:
        loop = asyncio.get_event_loop()
        def _call():
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as f:
                f.write(audio_bytes)
                tmp_path = f.name
            audio_file = open(tmp_path, "rb")
            try:
                # Ajusta según versión SDK — aquí es un ejemplo que puede necesitar adaptación
                resp = openai.Audio.transcribe("gpt-4o-mini-transcribe", audio_file)
                audio_file.close()
                return resp.get("text") if isinstance(resp, dict) else str(resp)
            except Exception:
                audio_file.close()
                raise
        text = await loop.run_in_executor(None, _call)
        if text:
            return text.strip()
        return None
    except Exception as e:
        logger.debug("Error en transcripción de audio: %s", e)
        return None

# ---------------------------
# BÚSQUEDA PRINCIPAL SOBRE EL CORPUS
# ---------------------------
def build_response_from_knowledge(prompt: str, allow_multi: bool = True, use_gpt_normalizer: bool = True) -> Optional[str]:
    full_text = ATM_KNOWLEDGE or ""
    if not full_text:
        return None

    qa_pairs = parse_qa_pairs(full_text)
    info_map = parse_offices_and_contacts(full_text)
    pnorm = _normalize_input(prompt)

    # Intenciones simples
    if re.search(r"tengo una pregunta|tengo una duda|puedo preguntar|quiero preguntar", pnorm):
        return MSG_ASK_PROMPT

    # Palabras clave prioritarias (respuestas directas)
    if re.search(r"pagar|pago|banco|bancos|pago en linea|pagar por internet|donde pagar|dónde pagar", pnorm):
        section = extract_section_from_variants(full_text, HEADING_VARIANTS.get("¿Puedo pagar por internet?", []))
        if section:
            return _format_block("Formas de pago en línea", section, EMOJI_MAP.get("pago"))

    if any(k in pnorm for k in ("horario", "horarios", "oficina", "oficinas", "dirección", "direccion", "whatsapp", "telefono", "teléfono", "contacto")):
        if "Horarios" in info_map and ("horario" in pnorm or "horarios" in pnorm):
            return _format_block("Horarios de atención", info_map["Horarios"], EMOJI_MAP.get("horario"))
        if "Oficinas" in info_map and any(x in pnorm for x in ("oficina", "oficinas", "dirección", "direccion", "sede")):
            return _format_block("Oficinas", info_map["Oficinas"], EMOJI_MAP.get("oficina"))
        if "Contacto" in info_map and any(x in pnorm for x in ("whatsapp", "telefono", "teléfono", "contacto", "pagina", "página")):
            return _format_block("Contacto y canales en línea", info_map["Contacto"], EMOJI_MAP.get("contacto"))

    # Coincidencia directa (exacta o contención)
    exact_matches = []
    for qa in qa_pairs:
        qnorm = _normalize_input(qa.get("question", ""))
        if not qnorm:
            continue
        if qnorm == pnorm or qnorm in pnorm or pnorm in qnorm:
            exact_matches.append((qa, 1.0))
    if exact_matches:
        if allow_multi and MULTI_ANSWER_ENABLED and len(exact_matches) > 1:
            return format_multi_answers(exact_matches)
        qa = exact_matches[0][0]
        return _format_block(qa.get("question", ""), qa.get("answer", ""), EMOJI_MAP.get("default"))

    # Similitud de secuencia frente a preguntas
    sim_results = []
    for qa in qa_pairs:
        q = qa.get("question", "")
        sim = sequence_similarity(pnorm, _normalize_input(q))
        sim_results.append((qa, sim))
    sim_results.sort(key=lambda x: x[1], reverse=True)
    if sim_results and sim_results[0][1] >= MIN_SIMILARITY_FOR_DIRECT_ANSWER:
        top_similar = [r for r in sim_results if r[1] >= MIN_SIMILARITY_FOR_DIRECT_ANSWER]
        if allow_multi and MULTI_ANSWER_ENABLED and len(top_similar) > 1:
            return format_multi_answers(top_similar)
        best_qa = sim_results[0][0]
        return _format_block(best_qa.get("question", ""), best_qa.get("answer", ""), EMOJI_MAP.get("default"))

    # Búsqueda semántica combinada
    sem_results = semantic_search(prompt, qa_pairs, top_n=5)
    if sem_results:
        top_qa, sc = sem_results[0]
        if sc >= SEMANTIC_SCORE_THRESHOLD:
            strong = [r for r in sem_results if r[1] >= SEMANTIC_SCORE_THRESHOLD]
            if allow_multi and MULTI_ANSWER_ENABLED and len(strong) > 1:
                return format_multi_answers(strong)
            suggestion = "\n\n*Si esto no responde, intente dar más detalles (número de registro, placa o periodo).*"
            return _format_block(top_qa.get("question", ""), top_qa.get("answer", "") + suggestion, EMOJI_MAP.get("default"))

    # Intentar refinamiento con GPT normalizer (solo reformulación)
    try:
        if use_gpt_normalizer and openai is not None and OPENAI_API_KEY:
            loop = asyncio.get_event_loop()
            norm = loop.run_until_complete(call_gpt_normalizer(prompt))
            if norm and isinstance(norm, dict):
                clarified = norm.get("clarified") or norm.get("clarified_question") or None
                keywords = norm.get("keywords") or None
                if clarified:
                    clar_norm = _normalize_input(clarified)
                    for qa in qa_pairs:
                        qnorm = _normalize_input(qa.get("question", ""))
                        if clar_norm == qnorm or clar_norm in qnorm or qnorm in clar_norm:
                            return _format_block(qa.get("question", ""), qa.get("answer", ""), EMOJI_MAP.get("default"))
                    best = None
                    bests = 0.0
                    for qa in qa_pairs:
                        s = sequence_similarity(clar_norm, _normalize_input(qa.get("question", "")))
                        if s > bests:
                            bests = s
                            best = qa
                    if best and bests >= 0.65:
                        return _format_block(best.get("question", ""), best.get("answer", ""), EMOJI_MAP.get("default"))
                if keywords:
                    kw_list = [k.strip() for k in re.split(r"[,\n;]+", keywords) if k.strip()]
                    scored = []
                    for qa in qa_pairs:
                        text = " ".join([qa.get("question", ""), qa.get("answer", "")]).lower()
                        score = sum(1 for kw in kw_list if kw.lower() in text)
                        if score > 0:
                            scored.append((qa, float(score)))
                    if scored:
                        scored.sort(key=lambda x: x[1], reverse=True)
                        if allow_multi and MULTI_ANSWER_ENABLED and len(scored) > 1:
                            return format_multi_answers(scored)
                        qa_top = scored[0][0]
                        return _format_block(qa_top.get("question", ""), qa_top.get("answer", ""), EMOJI_MAP.get("default"))
    except Exception as e:
        logger.debug("Error al usar normalizador GPT: %s", e)

    # búsqueda por encabezados variantes
    for heading, variants in HEADING_VARIANTS.items():
        for v in variants:
            if _normalize_input(v) in pnorm:
                section = extract_section_from_variants(full_text, variants)
                if section:
                    return _format_block(v.rstrip(":"), section, EMOJI_MAP.get("default"))

    return None

# ---------------------------
# HELPER: extracción por variantes de encabezado
# ---------------------------
def extract_section_from_variants(full_text: str, heading_variants: List[str]) -> str:
    text = full_text or ""
    for hv in heading_variants:
        hv_esc = re.escape(hv).replace(r"\¿", "¿").replace(r"\?", r"\?")
        pattern = re.compile(rf"(^|\n)\s*{hv_esc}\s*:?\s*\n", re.I)
        m = pattern.search(text)
        if m:
            start = m.end()
            next_heading = re.compile(r"\n[A-ZÁÉÍÓÚÑ0-9].{0,120}:\s*\n")
            nxt = next_heading.search(text, start)
            end = nxt.start() if nxt else len(text)
            return _clean(text[start:end])
    return ""

# ---------------------------
# HANDLER PRINCIPAL
# ---------------------------
class ATMInteligenciaHandler:
    """
    Handler principal para integrar con tu flujo de mensajería (WhatsApp).
    Uso:
        handler = ATMInteligenciaHandler(msg_handler=tu_msg_handler, atm_keyword="...") 
        await handler.handle_message(texto, numero, nombre, msg_id)
    """

    def __init__(self, msg_handler: Optional[Any] = None, atm_keyword: Optional[str] = None, use_gpt_for_reasoning: bool = True, enable_voice: bool = True):
        self.msg_handler = msg_handler
        self._atm_keyword = (atm_keyword or os.getenv("ATM_IA_KEYWORD", "prueba atm inteligencia")).strip().lower()
        self.use_gpt_for_reasoning = use_gpt_for_reasoning and openai is not None and bool(OPENAI_API_KEY)
        self.enable_voice = enable_voice
        self._qa_pairs = parse_qa_pairs(ATM_KNOWLEDGE or "")
        self._info_map = parse_offices_and_contacts(ATM_KNOWLEDGE or "")
        self._cache: Dict[str, Tuple[float, str]] = {}

    async def _save_state_and_history(self, numero: str, name: str, prompt: str, response: Optional[str]):
        try:
            user_state = await get_estado_usuario(numero) or {}
            ia_hist = user_state.get("ia_history", []) or []
            if prompt:
                ia_hist.append({"role": "user", "content": prompt})
            if response:
                ia_hist.append({"role": "assistant", "content": response})
            ia_hist = ia_hist[-30:]
            await set_estado_usuario(numero, {"contexto": "atm_ia", "estado": "conversando-ia", "ia_history": ia_hist})
            await registrar_historial(origen="IA", actor=name, numero=numero, texto=(prompt or "")[:2000])
            if response:
                await registrar_historial(origen="IA", actor="AMI", numero=numero, texto=(response)[:2000])
        except Exception as e:
            logger.warning("Error guardando estado/historial: %s", e)

    async def handle_message(self, texto: Any, numero: str, name: str, msg_id: str = "", is_voice: bool = False, voice_bytes: Optional[bytes] = None) -> List[Dict[str, Any]]:
        # Si es mensaje de voz y bytes provistos, intentar transcribir
        if is_voice and voice_bytes and self.enable_voice:
            try:
                transcribed = await transcribe_audio_bytes(voice_bytes)
                if transcribed:
                    texto = transcribed
                else:
                    return [{
                        "messaging_product": "whatsapp",
                        "to": numero,
                        "type": "text",
                        "text": {"body": "No pude transcribir tu mensaje de voz. Por favor, envíalo como texto."}
                    }]
            except Exception as e:
                logger.exception("Error transcribiendo voz: %s", e)
                return [{
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "text",
                    "text": {"body": "Ocurrió un error procesando el audio. Intenta enviar el mensaje como texto."}
                }]

        prompt_raw = str(texto or "")
        prompt = prompt_raw.strip()
        prompt_lower = _normalize_input(prompt)

        # validar gibberish
        if is_gibberish(prompt):
            try:
                await registrar_historial(origen="IA", actor=name, numero=numero, texto=f"ERROR_GIBBERISH: {prompt[:200]}")
            except Exception:
                pass
            return [{
                "messaging_product": "whatsapp", "to": numero, "type": "text",
                "text": {"body": MSG_NOT_UNDERSTOOD}
            }]

        # saludos -> salir / mostrar menu
        if prompt_lower in GREETINGS:
            try:
                await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": "", "feedback_id": ""})
            except Exception as e:
                logger.warning("Error limpiando estado (greeting): %s", e)
            try:
                await registrar_historial(origen="IA", actor=name, numero=numero, texto="COMANDO_GREET_EXIT")
            except Exception:
                pass
            if self.msg_handler:
                try:
                    return await self.msg_handler._show_main_menu(numero, name)
                except Exception as e:
                    logger.warning("Error mostrando menú desde handler (greeting): %s", e)
            return [{
                "messaging_product": "whatsapp", "to": numero, "type": "text",
                "text": {"body": "👋 Ha salido del modo de asistencia. Escriba *hola* para ver el menú."}
            }]

        # salir explícito
        if prompt_lower in EXIT_WORDS:
            try:
                await set_estado_usuario(numero, {"contexto": "", "estado": "", "ci": "", "mail": "", "feedback_id": ""})
            except Exception as e:
                logger.warning("Error limpiando estado al salir IA: %s", e)
            try:
                await registrar_historial(origen="IA", actor=name, numero=numero, texto="COMANDO_SALIR")
            except Exception:
                pass
            if self.msg_handler:
                try:
                    return await self.msg_handler._show_main_menu(numero, name)
                except Exception as e:
                    logger.warning("Error mostrando menú desde handler (salir): %s", e)
            return [{
                "messaging_product": "whatsapp", "to": numero, "type": "text",
                "text": {"body": "✔️ Ha salido del modo de asistencia. Escriba *hola* para ver el menú."}
            }]

        # bienvenida por keyword
        if prompt == "" or prompt_lower == self._atm_keyword:
            saludo = (
                f"👋 *BIENVENIDO, {name}*\n\n"
                "*AMI — ASISTENTE AUTOMATIZADO*\n\n"
                "¿En qué puedo ayudarle? Escriba su pregunta en lenguaje natural o envíe un mensaje de voz.\n"
                "Escriba *SALIR* para volver al menú."
            )
            try:
                await set_estado_usuario(numero, {"contexto": "atm_ia", "estado": "conversando-ia", "ci": "", "mail": ""})
            except Exception as e:
                logger.warning("Error guardando estado al entrar IA: %s", e)
            try:
                await registrar_historial(origen="IA", actor="AMI", numero=numero, texto=saludo[:2000])
            except Exception:
                pass
            return [{
                "messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": saludo}
            }]

        # quick intent detection
        if re.search(r"tengo una pregunta|tengo una duda|puedo preguntar|quiero preguntar", _normalize_input(prompt)):
            try:
                await registrar_historial(origen="IA", actor=name, numero=numero, texto="USER_ASK_INTENT_DETECTED")
            except Exception:
                pass
            return [{
                "messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": MSG_ASK_PROMPT}
            }]

        # cache lookup
        cache_key = f"q:{_normalize_input(prompt)}"
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached[0] < CACHE_TTL_SECONDS):
            content = cached[1]
        else:
            try:
                content = build_response_from_knowledge(prompt, allow_multi=True, use_gpt_normalizer=self.use_gpt_for_reasoning)
            except Exception as e:
                logger.exception("Error procesando knowledge: %s", e)
                content = None
            self._cache[cache_key] = (time.time(), content or "")

        if content:
            try:
                await self._save_state_and_history(numero, name, prompt, content)
            except Exception:
                pass
            return [{
                "messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": content}
            }]

        # no coverage
        try:
            await set_estado_usuario(numero, {"contexto": "atm_ia", "estado": "conversando-ia"})
            await registrar_historial(origen="IA", actor=name, numero=numero, texto=f"NO_COVERAGE_PROMPT: {prompt[:200]}")
        except Exception:
            pass

        return [{
            "messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": MSG_NO_COVERAGE}
        }]

# Alias para compatibilidad (si tu código importaba V2 antes)
ATMInteligenciaHandlerV2 = ATMInteligenciaHandler

# ---------------------------
# FIN DEL ARCHIVO
# ---------------------------
