from pydantic import BaseModel


class ReservaCreate(BaseModel):
    id_mesa: int
    fecha: str
    hora: str
    personas: int


class ReservaResponse(BaseModel):
    id: int
    fecha: str
    hora: str
    personas: int
    estado: str
    mesa: str
    restaurante: str