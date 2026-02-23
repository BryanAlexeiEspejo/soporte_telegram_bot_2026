# app/services/handlers/catastro/D_3_info_catastro_3_p2.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

MAX_DESC = 72
def _short(s: str, n: int = MAX_DESC) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

async def manejar_info_catastro_3_p2(numero: str) -> List[Dict]:
    # 🧾 Cuerpo con las preguntas 9–12 “tal cual”
    cuerpo = (
        "------------------------------\n"
        "*Registro y documentación catastral (pág. 2)*\n"
        "9. ¿Qué tipos de documentos puedo solicitar en copia simple o legalizada en el archivo de catastro?\n"
        "10. ¿Puedo solicitar una copia original de mi certificado catastral?\n"
        "11. ¿Cuál es el procedimiento para solicitar fotocopias legalizadas de levantamientos topográficos?\n"
        "12. ¿Es obligatorio usar el Formulario Único de Solicitud (FUS) para todos los trámites en el archivo de catastro?\n"
        "------------------------------\n"
        "Selecciona una opción:"
    )

    q9  = "¿Qué tipos de documentos puedo solicitar en copia simple o legalizada en el archivo de catastro?"
    q10 = "¿Puedo solicitar una copia original de mi certificado catastral?"
    q11 = "¿Cuál es el procedimiento para solicitar fotocopias legalizadas de levantamientos topográficos?"
    q12 = "¿Es obligatorio usar el Formulario Único de Solicitud (FUS) para todos los trámites en el archivo de catastro?"

    # 4 preguntas + Volver + Inicio = 6 filas total ✅
    secciones = [{
        "title": "Opciones",
        "rows": [
            {"id": "q-catastro-3-9",  "title": "9",  "description": _short(q9)},
            {"id": "q-catastro-3-10", "title": "10", "description": _short(q10)},
            {"id": "q-catastro-3-11", "title": "11", "description": _short(q11)},
            {"id": "q-catastro-3-12", "title": "12", "description": _short(q12)},
            {"id": "info-catastro-3", "title": "⬅️ Volver (1–8)", "description": "Regresar a la página 1"},
            {"id": "inicio", "title": "🏠 Inicio", "description": "Ir al menú principal"},
        ]
    }]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Ver preguntas"
    )

    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "info-catastro-3-p2"})
    return [payload]
