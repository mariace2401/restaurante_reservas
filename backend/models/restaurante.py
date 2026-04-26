from pydantic import BaseModel
from typing import Optional


class HorarioSchema(BaseModel):
    dia: str
    apertura: str
    cierre: str


class MesaSchema(BaseModel):
    id_mesa: int
    numero: int
    capacidad: int


class RestauranteResponse(BaseModel):
    id: int
    nombre: str
    direccion: str
    telefono: str
    descripcion: str
    administrador: str
    horarios: list[HorarioSchema] = []
    mesas_disponibles: list[MesaSchema] = []


class Restaurante_listResponse(BaseModel):
    id: int
    nombre: str
    direccion: str
    telefono: str
    descripcion: str
    administrador: str

    