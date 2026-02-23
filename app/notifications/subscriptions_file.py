import os
import json
import asyncio
import tempfile
from typing import Dict, List, Optional, Tuple

LOCK = asyncio.Lock()
BASE_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(BASE_DIR, exist_ok=True)

SUBSCRIPTIONS_PATH = os.path.join(BASE_DIR, "subscriptions.json")
LAST_STATES_PATH = os.path.join(BASE_DIR, "subscriptions_last_states.json")


def _ensure_file(path: str, default):
    if not os.path.exists(path):
        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8", dir=BASE_DIR)
        try:
            json.dump(default, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.file.fileno())
        finally:
            tmp.close()
            os.replace(tmp.name, path)


async def _read_file(path: str) -> Optional[dict]:
    _ensure_file(path, {})
    async with LOCK:
        try:
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    return {}
                except Exception:
                    return {}
        except FileNotFoundError:
            return {}


async def _write_file(path: str, data: dict):
    async with LOCK:
        fd, tmp_name = tempfile.mkstemp(dir=BASE_DIR, prefix="tmp_", suffix=".json")
        tmp = os.fdopen(fd, "w", encoding="utf-8")
        try:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
            os.replace(tmp_name, path)
        finally:
            if not tmp.closed:
                tmp.close()


# -------------------------
# Subscriptions API
# -------------------------
async def add_subscription_file(codigo: str, chat_id: str):
    codigo = str(codigo)
    chat_id = str(chat_id)
    data = await _read_file(SUBSCRIPTIONS_PATH) or {}
    lst = data.get(codigo, [])
    if not isinstance(lst, list):
        lst = []
    if chat_id not in lst:
        lst.append(chat_id)
        data[codigo] = lst
        await _write_file(SUBSCRIPTIONS_PATH, data)


async def remove_subscription_file(codigo: str, chat_id: str) -> bool:
    codigo = str(codigo)
    chat_id = str(chat_id)
    data = await _read_file(SUBSCRIPTIONS_PATH) or {}
    lst = data.get(codigo, [])
    if not isinstance(lst, list):
        lst = []
    if chat_id in lst:
        lst.remove(chat_id)
        if lst:
            data[codigo] = lst
        else:
            data.pop(codigo, None)
        await _write_file(SUBSCRIPTIONS_PATH, data)
        return True
    return False


async def get_subscribers_file(codigo: str) -> List[str]:
    codigo = str(codigo)
    data = await _read_file(SUBSCRIPTIONS_PATH) or {}
    lst = data.get(codigo, [])
    return list(lst) if isinstance(lst, list) else []


async def list_all_codes() -> List[str]:
    data = await _read_file(SUBSCRIPTIONS_PATH) or {}
    return list(data.keys())


async def list_all_subscriptions_pairs() -> List[Tuple[str, str]]:
    data = await _read_file(SUBSCRIPTIONS_PATH) or {}
    pairs = []
    for code, lst in data.items():
        if isinstance(lst, list):
            for chat in lst:
                pairs.append((code, chat))
    return pairs


# -------------------------
# Last-states persistence (para detectar cambios)
# -------------------------
async def _get_last_states() -> Dict[str, str]:
    data = await _read_file(LAST_STATES_PATH) or {}
    # normalizar a strings
    return {str(k): str(v) for k, v in data.items()}


async def _set_last_state(codigo: str, estado: Optional[str]):
    codigo = str(codigo)
    last = await _get_last_states()
    if estado is None:
        last.pop(codigo, None)
    else:
        last[codigo] = str(estado)
    await _write_file(LAST_STATES_PATH, last)


async def get_last_state(codigo: str) -> Optional[str]:
    last = await _get_last_states()
    return last.get(str(codigo))


async def clear_all_last_states():
    await _write_file(LAST_STATES_PATH, {})

