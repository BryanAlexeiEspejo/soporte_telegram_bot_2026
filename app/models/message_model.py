from pydantic import BaseModel, Field, constr
from typing import Optional
from datetime import date

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    hostname: str

class Reservas(BaseModel):
    id: Optional[str] = Field(alias="_id")
    numero: str
    placa: str
    parqueo: str
    estado: str
    horaInicio: str
    horaFin: str
    fechaRegistro: date

class notificationRequest(BaseModel):
    mensaje: str
    numero: str

class PlacaUpdateRequest(BaseModel):
    placa: constr(strip_whitespace=True, min_length=5, max_length=20) # type: ignore