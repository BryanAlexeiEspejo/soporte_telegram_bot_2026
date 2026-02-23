# app/services/handlers/atm/A_5_consecuencias_sanciones.py
from typing import List, Dict
from app.database.database import set_estado_usuario

# ✅ 5. Más información — TODO en un solo mensaje (INTERACTIVE LIST) + Navegación
# Nota: Se construye el payload manualmente para NO enviar header/footer vacíos.
async def manejar_consecuencias_sanciones(numero: str) -> List[Dict]:
    body_text = (
        "*Más información*\n"
        "Consulta canales oficiales de atención.\n\n"
        "*📍 Consultas presenciales*\n"
        "*OFICINA CENTRAL*\n"
        "Edif. Armando Escobar Uría – Ex Banco del Estado, Calle Mercado  Nº 1298 esq. Calle Colon – ADMINISTRACIÓN TRIBUTARIA MUNICIPAL\n\n"
        "*🕒 Horario de atención*\n"
        "• Lunes a viernes: 08:00 a 19:00\n"
        "• Sábados: 08:00 a 13:00\n\n"
        "*- OFICINA 1*\n\n"
        "Zona de Calacoto Av. Ballivian entre calles 13 y 14, edif. Atlanta PB Plataforma Sermat – PIAC – Sur.\n"
        "Horario de Atención: Lunes a Viernes de 09:00 a 17:00\n\n"
        "*- OFICINA 2*\n\n"
        "Platoforma Integral de atención Ciudadana PIAC, Mercado Camacho Nivel 1.\n"
        "Horario de Atención: Lunes a viernes de 09:30 a 17:30\n\n"
        "*🌐 Consultas en línea*\n"
        "🔗 www.ruat.gob.bo\n\n"
        "*📱 Escríbenos al WhatsApp*\n"
        "📞 62443034 – 71552352\n\n"
        "*☎️ Línea gratuita*\n"
        "155 (opción 2)\n\n"
        "*🏛️ Página oficial Administración Tributaria Municipal – ATM*\n"
        "🔗 http://atm.lapaz.bo:3725/#/inicio\n\n"
        "*🎵 TikTok oficial*\n"
        "🔗 https://www.tiktok.com/@atm.la.paz\n\n"
       
    )

    payload_interactive: Dict = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            # ⚠️ Sin header/footer para evitar (#131009) cuando están vacíos o None
            "body": {"text": body_text},
            "action": {
                "button": "Ver opciones",
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

    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-5"})
    return [payload_interactive]
