from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, APIRouter
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel


SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def crear_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def obtener_usuario(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    usuario = obtener_usuario(token)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return usuario


# ==============================
# ROUTER
# ==============================
router = APIRouter()


# ==============================
# MODELO
# ==============================
class User(BaseModel):
    username: str
    password: str


# ==============================
# "BASE DE DATOS" TEMPORAL
# ==============================
usuarios = []


# ==============================
# REGISTER
# ==============================
@router.post("/auth/register")
def register(user: User):
    for u in usuarios:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

    usuarios.append({
        "username": user.username,
        "password": user.password
    })

    return {"message": "Usuario registrado correctamente"}


# ==============================
# LOGIN
# ==============================
@router.post("/auth/login")
def login(user: User):
    for u in usuarios:
        if u["username"] == user.username and u["password"] == user.password:
            token = crear_token({"sub": user.username})
            return {"access_token": token}

    raise HTTPException(status_code=401, detail="Credenciales incorrectas")