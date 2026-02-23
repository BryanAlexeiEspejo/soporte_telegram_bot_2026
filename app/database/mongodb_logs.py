from app.models.message_model import Reservas
from app.database.database import db
from datetime import datetime


def extraer_con_find(texto: str) -> dict:
    try:
        texto = texto.lower().replace("\n", " ")  # Elimina saltos de línea

        placa_key = "mi placa es:"
        parqueo_key = "el parqueo es:"
        hora_ini_key = "hora inicio:"
        hora_fin_key = "hora fin:"

        placa_inicio = texto.find(placa_key)
        parqueo_inicio = texto.find(parqueo_key)
        hora_inicio = texto.find(hora_ini_key)
        hora_fin = texto.find(hora_fin_key)

        if -1 in [placa_inicio, parqueo_inicio, hora_inicio, hora_fin]:
            raise ValueError("Faltan campos requeridos en el texto.")

        placa = texto[placa_inicio + len(placa_key):parqueo_inicio].strip()
        parqueo = texto[parqueo_inicio + len(parqueo_key):hora_inicio].strip()
        hora_ini = texto[hora_inicio + len(hora_ini_key):hora_fin].strip()
        hora_fin_valor = texto[hora_fin + len(hora_fin_key):].strip()

        return {
            "placa": placa,
            "parqueo": parqueo,
            "hora_inicio": hora_ini,
            "hora_fin": hora_fin_valor
        }

    except Exception as e:
        print(f"❌ Error al extraer datos: {e}")
        return None


def register_parking_reservations(numero: str, texto: str,nombre: str):
    valores = extraer_con_find(texto)

    if not valores:
        print("❌ No se pudo registrar la reserva por error en el texto.")
        return

    reserva_data = {
        "name":nombre,
        "numero": numero,
        "placa": valores["placa"],
        "parqueo": valores["parqueo"],
        "estado": "PREREGISTRO",
        "horaInicio": valores["hora_inicio"],
        "horaFin": valores["hora_fin"],
        "fechaRegistro": datetime.utcnow()
    }

    try:
        db.reservas.insert_one(reserva_data)
        print("✅ Reserva registrada con ID:")
        return True        
    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")
        return False