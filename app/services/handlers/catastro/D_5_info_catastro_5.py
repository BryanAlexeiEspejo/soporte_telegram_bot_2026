# app/services/handlers/catastro/D_5_info_catastro_5.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

# ✅ LIST con secciones (Preguntas + Navegación)
async def manejar_info_catastro_5(numero: str) -> List[Dict]:
    # Cuerpo con las preguntas “tal cual”
    cuerpo = (
        "------------------------------\n"
        "*Herencias, copropiedades y terceros*\n"
        "1. ¿Cómo puedo obtener información de una vivienda que no es mi propiedad?\n"
        "2. ¿Puedo realizar el trámite en nombre de una tercera persona?\n"
        "3. ¿Puedo solicitar información o copias de documentos si soy un heredero del propietario original?\n"
        "4. ¿Qué debo hacer si hay contradicciones en los documentos de propiedad debido a un divorcio?\n"
        "5. ¿Puede un copropietario solicitar información o copias de documentos sin la presencia de los otros copropietarios?\n"
        "6. ¿Qué documentos debo presentar si solicito información catastral en nombre de una empresa?\n"
        "------------------------------\n"
        "Selecciona una opción:"
    )

    q1 = "¿Cómo puedo obtener información de una vivienda que no es mi propiedad?"
    q2 = "¿Puedo realizar el trámite en nombre de una tercera persona?"
    q3 = "¿Puedo solicitar información o copias de documentos si soy un heredero del propietario original?"
    q4 = "¿Qué debo hacer si hay contradicciones en los documentos de propiedad debido a un divorcio?"
    q5 = "¿Puede un copropietario solicitar información o copias de documentos sin la presencia de los otros copropietarios?"
    q6 = "¿Qué documentos debo presentar si solicito información catastral en nombre de una empresa?"

    secciones = [
        {
            "title": "Preguntas (1–6)",
            "rows": [
                {"id": "q-catastro-5-1", "title": "1", "description": _short(q1)},
                {"id": "q-catastro-5-2", "title": "2", "description": _short(q2)},
                {"id": "q-catastro-5-3", "title": "3", "description": _short(q3)},
                {"id": "q-catastro-5-4", "title": "4", "description": _short(q4)},
                {"id": "q-catastro-5-5", "title": "5", "description": _short(q5)},
                {"id": "q-catastro-5-6", "title": "6", "description": _short(q6)},
            ],
        },
        {
            "title": "Navegación",
            "rows": [
                {"id": "catastro-d", "title": "⬅️ Menú anterior", "description": "Volver a preguntas frecuentes"},
                {"id": "inicio",     "title": "🏠 Inicio",        "description": "Ir al menú principal"},
            ],
        },
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Ver preguntas"
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "info-catastro-5"})
    return [payload]
