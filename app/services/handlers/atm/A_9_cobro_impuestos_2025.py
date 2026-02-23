# app/services/handlers/atm/A_9_cobro_impuestos_2025.py
from typing import List, Dict
from app.database.database import set_estado_usuario
from app.services.whatsapp_template import crear_payload_lista


# ✅ 9. Cobro de impuestos gestión 2025
async def manejar_cobro_impuestos_2025(numero: str) -> List[Dict]:
    mensajes: List[Dict] = []

    # ─────────────────────────────────────────────
    # 1) MENSAJE DE TEXTO — INFORMACIÓN COMPLETA
    # ─────────────────────────────────────────────
    body_text = (
        "*COBRO DE IMPUESTOS MUNICIPALES – GESTIÓN 2025*\n\n"
        "Desde el *martes 6 de enero de 2026* se inicia el cobro de los impuestos municipales a la propiedad "
        "de bienes inmuebles y vehículos correspondientes a la gestión 2025, conforme a la "
        "*Resolución Administrativa N.º 16/2025 (27/12/2025).* \n\n"

        "*DESCUENTO POR PRONTO PAGO*\n"
        "✔️ 15 % de descuento por pago al contado gestión 2025\n"
        "✔️ Válido para inmuebles y vehículos\n\n"

        "*PLAZO DEL BENEFICIO*\n"
        "📅 Desde el 6 de enero hasta el 19 de febrero de 2026\n"
        "🕒 45 días sin multas ni intereses\n\n"

        "*EVITE FILAS Y AGLOMERACIONES*\n"
        "Le recomendamos no esperar hasta el último día y realizar su pago con anticipación en los puntos "
        "de recaudación habilitados.\n\n"

        "*COMPROMISO MUNICIPAL*\n"
        "El Gobierno Municipal reafirma su compromiso de facilitar el cumplimiento tributario e invita a la "
        "ciudadanía a aprovechar este beneficio dentro del plazo establecido.\n\n"

        "*¿Desea saber cómo pagar, dónde hacerlo o consultar su deuda?*\n\n"

        "*PUNTOS DE PAGO:*\n"
        "- En las diferentes entidades financieras a nivel nacional\n"
        "- Cajas de oficinas de la Administración Tributaria Municipal de la Ciudad de La Paz\n\n"

        "*CÓMO PAGAR:*\n"
        "- Puedes pagar con el número de registro del inmueble o número de placa del vehículo\n"
        "- Obteniendo el código QR a través de www.ruat.gob.bo\n\n"

        "*Fuente actualizada hasta:*\nEne. 14 por Yesid Flores Huayhua (ATM)"
    )

    payload_texto = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "body": body_text,
            "preview_url": False
        },
    }

    mensajes.append(payload_texto)

   
    cuerpo_vacio = "\u200B"  

    secciones = [
        {
            "title": "Navegación",
            "rows": [
                {
                    "id": "atm-menu",
                    "title": "🏛️ Menú ATM",
                    "description": "Volver a Administración Tributaria Municipal"
                },
                {
                    "id": "inicio",
                    "title": "🏠 Inicio",
                    "description": "Ir al menú principal"
                },
            ],
        }
    ]

    payload_lista = await crear_payload_lista(
        numero=numero,
        cuerpo=cuerpo_vacio,              
        opciones=secciones,
        header_text="",                  
        footer_text="", 
        button_text="Ver opciones",       
    )

    mensajes.append(payload_lista)

    # Guardar estado
    await set_estado_usuario(numero, {"contexto": "atm", "estado": "atm-9"})

    return mensajes
