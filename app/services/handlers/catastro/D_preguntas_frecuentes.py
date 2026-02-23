# app/services/handlers/catastro/D_preguntas_frecuentes.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista

async def manejar_preguntas_frecuentes(numero: str) -> List[Dict]:
    # Cuerpo ÚNICO (texto intro + llamado a acción)
    cuerpo = (
        "🎯 *Objetivo*\n"
        "• *Público general:* horarios, ubicación, requisitos y derivación.\n"
        "• *Propietarios:* certificados, actualizaciones, observaciones y seguimiento.\n"
        "• *Arquitectos:* revisión de documentación, levantamientos, puntos topográficos, "
        "medidas y permisos.\n"
    )

    # Menú: títulos ≤24 y descripciones concisas
    secciones = [
        {
            "title": "📚 Preguntas frecuentes",
            "rows": [
                {
                    "id": "info-catastro-1",
                    "title": "1. Info general",
                    "description": "Incluye horarios, ubicación y requisitos generales."
                },
                {
                    "id": "info-catastro-2",
                    "title": "2. Atención al ciudadano",
                    "description": "Redirección a áreas competentes y aspectos de atención."
                },
                {
                    "id": "info-catastro-3",
                    "title": "3. Registro y doc.",
                    "description": "Relacionado con certificados, actualizaciones y observaciones."
                },
                {
                    "id": "info-catastro-4",
                    "title": "4. Actualización/datos",
                    "description": "Cambios o correcciones necesarias en los datos catastrales."
                },
                {
                    "id": "info-catastro-5",
                    "title": "5. Herencias y terceros",
                    "description": "Trámites específicos para propietarios y sus representantes."
                },
                {
                    "id": "info-catastro-6",
                    "title": "6. Trámites/procedim.",
                    "description": "Incluye revisión de documentación y solicitudes específicas."
                },
                {
                    "id": "info-catastro-7",
                    "title": "7. Requisitos y permisos",
                    "description": "Relacionado con puntos topográficos, medidas y permisos necesarios."
                },
            ]
        },
        {
            "title": "🔁 Navegación",
            "rows": [
                {
                    "id": "catastro-b",
                    "title": "⬅️ Menú anterior",
                    "description": "Volver atrás"
                },
                {
                    "id": "inicio",
                    "title": "🏠 Inicio",
                    "description": "Menú principal"
                }
            ]
        }
    ]

    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="",
        footer_text="",
        button_text="Preguntas frecuentes"   # ≤ 20 caracteres
    )

    await set_estado_usuario(numero, {
        "contexto": "catastro",
        "estado": "preguntas-frecuentes"
    })

    return [payload]
