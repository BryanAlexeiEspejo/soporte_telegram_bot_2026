# app/services/handlers/atm/A_4_casos_especiales.py
from typing import List, Dict
from app.database.database import set_estado_usuario

# ✅ 4. No pierdas la oportunidad — TODO en un solo mensaje (INTERACTIVE LIST)
async def manejar_casos_especiales(numero: str) -> List[Dict]:
    body_text = (
     
       
        "*¿Qué pasa si no me acojo a la Ley?*\n"
        "    R. Si dejas pasar esta oportunidad y no regularizas tu deuda tributaria hasta la vigencia de la Ley, perderás todos los beneficios de la Ley. Esto significa que volverás a tener que pagar intereses, multas y sanciones, además de que se iniciarán los procesos de cobro.\n\n"
        "*Selecciona una opción:*"
    )

    payload_interactive: Dict = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            
            "body": {"text": body_text},
            "action": {
                "button": "Opciones disponibles",
                "sections": [
                    {
                        "title": "Navegación",
                        "rows": [
                            {
                                "id": "atm-menu",
                                "title": "🏛️ Menú anterior",
                                "description": "Volver a Administración Tributaria Municipal – ATM",
                            },
                            {
                                "id": "inicio",
                                "title": "🏠 Inicio",
                                "description": "Ir al menú principal",
                            },
                        ],
                    }
                ],
            },
        },
    }

    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-4"})
    return [payload_interactive]
