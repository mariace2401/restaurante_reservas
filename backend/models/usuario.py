from pydantic import BaseModel


class Login(BaseModel):
    correo: str
    password: str


class UsuarioCreate(BaseModel):
    nombre: str
    correo: str
    password: str


class TokenResponse(BaseModel):
    mensaje: str
    access_token: str | None = None
    rol: str | None = None