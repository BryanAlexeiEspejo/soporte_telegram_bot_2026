# app/services/handlers/catastro/E_contactos_direcciones.py
from typing import List, Dict
from app.services.whatsapp_template import crear_payload_lista
from app.database.database import set_estado_usuario

async def manejar_contactos_direcciones(numero: str) -> List[Dict]:
    # Cuerpo ÚNICO (todo el panel naranja)
    cuerpo = (
        "✅ *Autoridad Catastral Municipal (ACM):* Ing. Carlos Jose Medrano Rodríguez.\n\n"
        "📍 *Ubicación de Catastro:* Edif. *Tobia*, planta baja, *calle Potosí y Colón*.\n"
        "🔗 Mapa: https://maps.app.goo.gl/a1rLTvYm5pUhCN5Q8\n\n"
        "✅ *Reunirme con el técnico:*\n"
        "Dirígete a la *plataforma de atención* (Tobia, PB) y solicita *ficha para consultas especializadas*.\n"
        "🕘 8:45–16:15 (continuo).\n\n"
        "✅ *Audiencia con la ACM:*\n"
        "Se agenda por *correspondencia ciudadana*. Presenta *nota simple* en *SITRAM* "
        "(Potosí, Edif. Tobia, PB) de *lun–vie 8:45–16:10*.\n"
        "📥 *Nota modelo:* http://35.232.232.3:4002/NOTA_DE_SOLICITUD_DE_AUDIENCIA.docx\n"
        "────────────────────────\n"
        "Selecciona una opción para continuar:"
    )

    # Sección única: Navegación (títulos <= 24 caracteres)
    secciones = [
        {
            "title": "🔁 Navegación",
            "rows": [
                {
                    "id": "catastro-b",
                    "title": "⬅️ Volver",
                    "description": "Volver a información catastral",
                },
                {
                    "id": "inicio",
                    "title": "🏠 Volver al inicio",
                    "description": "Ir al menú principal",
                },
            ],
        }
    ]

    # Un solo payload (lista interactiva)
    payload = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo,
        opciones=secciones,
        header_text="📞 Contactos y direcciones",
        footer_text="",
        button_text="Opciones disponibles",  # ≤ 20 caracteres (más seguro)
    )

    # Quedamos listos para que el handler capture A–E o 'inicio'
    await set_estado_usuario(numero, {"contexto": "catastro", "estado": "esperando-opcion"})
    return [payload]
