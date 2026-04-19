from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Header, HTTPException, FastAPI
from pydantic import BaseModel
from typing import Optional
import psycopg2
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from jose import JWTError

app = FastAPI()

SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# MODELOS
# =========================

class Login(BaseModel):
    correo: str
    password: str


class UsuarioCreate(BaseModel):
    nombre: str
    correo: str
    password: str


class Reserva(BaseModel):
    id_mesa: int
    fecha: str
    hora: str
    personas: int


# =========================
# CONEXIÓN BD
# =========================

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="reservibe",
        user="postgres",
        password="1234",
        port="5432"
    )


# =========================
# JWT
# =========================

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def obtener_usuario(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data
    except JWTError:
        return None


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    usuario = obtener_usuario(token)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return usuario

# =========================
# REGISTRO
# =========================

@app.post("/registro")
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
        return {"mensaje": "Error o correo ya existe"}

    conexion.close()
    return {"mensaje": "Usuario creado"}


# =========================
# LOGIN
# =========================

@app.post("/login")
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
        return {"mensaje": "Usuario no existe"}

    password_ingresada = datos.password.encode('utf-8')
    password_guardada = usuario[3].encode('utf-8')

    if not bcrypt.checkpw(password_ingresada, password_guardada):
        return {"mensaje": "Credenciales incorrectas"}

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

# =========================
# RESTAURANTES
# =========================
 
@app.get("/restaurantes")
def listar_restaurantes():
    conexion = get_connection()
    cursor = conexion.cursor()
 
    cursor.execute("""
        SELECT r.id, r.nombre, r.direccion, r.telefono, r.descripcion,
               u.nombre AS administrador
        FROM restaurante r
        JOIN usuarios u ON r.id_usuario = u.id
    """)
    datos = cursor.fetchall()
    conexion.close()
 
    return [
        {
            "id": fila[0],
            "nombre": fila[1],
            "direccion": fila[2],
            "telefono": fila[3],
            "descripcion": fila[4],
            "administrador": fila[5]
        }
        for fila in datos
    ]

@app.get("/restaurantes/{id_restaurante}")
def detalle_restaurante(id_restaurante: int):
    conexion = get_connection()
    cursor = conexion.cursor()
 
    # Info del restaurante
    cursor.execute("""
        SELECT r.id, r.nombre, r.direccion, r.telefono, r.descripcion,
               u.nombre AS administrador
        FROM restaurante r
        JOIN usuarios u ON r.id_usuario = u.id
        WHERE r.id = %s
    """, (id_restaurante,))
    restaurante = cursor.fetchone()
 
    if restaurante is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
 
    # Horarios
    cursor.execute("""
        SELECT dia_semana, hora_apertura, hora_cierre
        FROM horario
        WHERE id_restaurante = %s
        ORDER BY CASE dia_semana
            WHEN 'lunes' THEN 1 WHEN 'martes' THEN 2 WHEN 'miércoles' THEN 3
            WHEN 'jueves' THEN 4 WHEN 'viernes' THEN 5
            WHEN 'sábado' THEN 6 WHEN 'domingo' THEN 7
        END
    """, (id_restaurante,))
    horarios = cursor.fetchall()
 
    # Mesas disponibles
    cursor.execute("""
        SELECT id, numero_mesa, capacidad
        FROM mesa
        WHERE id_restaurante = %s AND disponible = TRUE
    """, (id_restaurante,))
    mesas = cursor.fetchall()
    conexion.close()
 
    return {
        "id": restaurante[0],
        "nombre": restaurante[1],
        "direccion": restaurante[2],
        "telefono": restaurante[3],
        "descripcion": restaurante[4],
        "administrador": restaurante[5],
        "horarios": [
            {"dia": h[0], "apertura": str(h[1]), "cierre": str(h[2])}
            for h in horarios
        ],
        "mesas_disponibles": [
            {"id_mesa": m[0], "numero": m[1], "capacidad": m[2]}
            for m in mesas
        ]
    }



# =========================
# RESERVAS (PROTEGIDAS)
# =========================

@app.post("/reservas")
def crear_reserva(reserva: Reserva, usuario=Depends(get_current_user)):
    conexion = get_connection()
    cursor = conexion.cursor()
 
    # Verificar que la mesa existe y está disponible
    cursor.execute(
        "SELECT capacidad, disponible FROM mesa WHERE id = %s",
        (reserva.id_mesa,)
    )
    mesa = cursor.fetchone()
 
    if mesa is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
 
    if not mesa[1]:
        conexion.close()
        raise HTTPException(status_code=400, detail="La mesa no está disponible")
 
    if reserva.personas > mesa[0]:
        conexion.close()
        raise HTTPException(
            status_code=400,
            detail=f"La mesa tiene capacidad para {mesa[0]} personas"
        )
 
    try:
        cursor.execute(
            """INSERT INTO reservas (usuario_id, id_mesa, fecha, hora, personas, estado)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (usuario["id"], reserva.id_mesa, reserva.fecha, reserva.hora, reserva.personas, "pendiente")
        )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()
 
    return {"mensaje": "Reserva creada correctamente"}

@app.get("/mis-reservas")
def mis_reservas(usuario=Depends(get_current_user)):
    conexion = get_connection()
    cursor = conexion.cursor()
 
    cursor.execute("""
        SELECT r.id, r.fecha, r.hora, r.personas, r.estado,
               m.numero_mesa, res.nombre AS restaurante
        FROM reservas r
        JOIN mesa m ON r.id_mesa = m.id
        JOIN restaurante res ON m.id_restaurante = res.id
        WHERE r.usuario_id = %s
        ORDER BY r.fecha DESC, r.hora DESC
    """, (usuario["id"],))
 
    datos = cursor.fetchall()
    conexion.close()
 
    return [
        {
            "id": fila[0],
            "fecha": str(fila[1]),
            "hora": str(fila[2]),
            "personas": fila[3],
            "estado": fila[4],
            "mesa": fila[5],
            "restaurante": fila[6]
        }
        for fila in datos
    ]
 


@app.delete("/reservas/{id_reserva}")
def cancelar_reserva(id_reserva: int, usuario=Depends(get_current_user)):
    conexion = get_connection()
    cursor = conexion.cursor()
 
    cursor.execute(
        "SELECT usuario_id, estado FROM reservas WHERE id = %s",
        (id_reserva,)
    )
    reserva = cursor.fetchone()
 
    if reserva is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
 
    if reserva[0] != usuario["id"] and usuario["rol"] != "admin":
        conexion.close()
        raise HTTPException(status_code=403, detail="No tienes permiso para cancelar esta reserva")
 
    if reserva[1] == "cancelada":
        conexion.close()
        raise HTTPException(status_code=400, detail="La reserva ya está cancelada")
 
    try:
        cursor.execute(
            "UPDATE reservas SET estado = 'cancelada' WHERE id = %s",
            (id_reserva,)
        )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()
 
    return {"mensaje": "Reserva cancelada correctamente"}
