from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Login(BaseModel):
    correo: str
    password: str


class UsuarioCreate(BaseModel):
    nombre: str
    correo: str
    password: str


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    password: Optional[str] = None


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    fecha: Optional[str] = None


class TokenResponse(BaseModel):
    mensaje: str
    access_token: str | None = None
    rol: str | None = None