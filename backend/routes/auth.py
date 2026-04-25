from fastapi import APIRouter, HTTPException
from backend.database import get_connection
from backend.auth import crear_token
from backend.models.usuario import Login, UsuarioCreate, TokenResponse
import bcrypt


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro")
def registro(datos: UsuarioCreate):
    conexion = get_connection()
    cursor = conexion.cursor()
    password = datos.password.encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    hashed_str = hashed.decode('utf-8')

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, password) VALUES (%s, %s, %s)",
            (datos.nombre, datos.correo, hashed_str)
        )
        conexion.commit()
    except:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="Error o correo ya existe")
    finally:
        conexion.close()

    return {"mensaje": "Usuario creado"}


@router.post("/login", response_model=TokenResponse)
def login(datos: Login):
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id, nombre, correo, password, rol FROM usuarios WHERE correo = %s",
        (datos.correo.strip(),)
    )

    usuario = cursor.fetchone()
    conexion.close()

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no existe")

    password_ingresada = datos.password.encode('utf-8')
    password_guardada = usuario[3].encode('utf-8')

    if not bcrypt.checkpw(password_ingresada, password_guardada):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = crear_token({
        "id": usuario[0],
        "nombre": usuario[1],
        "correo": usuario[2],
        "rol": usuario[4]
    })

    return {
        "mensaje": "Login exitoso",
        "access_token": token,
        "rol": usuario[4]
    }