from pydantic import BaseModel
from typing import Optional


class HorarioInput(BaseModel):
    dia: str
    apertura: str
    cierre: str


class SolicitudCreate(BaseModel):
    nombre_restaurante: str
    telefono: Optional[str] = None
    direccion: str
    descripcion: Optional[str] = None
    num_mesas: int
    capacidad_mesas: int
    horarios: list[HorarioInput] = []


class SolicitudResponse(BaseModel):
    id: int
    id_usuario: int
    nombre_usuario: str
    correo_usuario: str
    nombre_restaurante: str
    telefono: Optional[str] = None
    direccion: str
    descripcion: Optional[str] = None
    num_mesas: int
    capacidad_mesas: int
    horarios: list = []
    estado: str
    fecha_solicitud: str
