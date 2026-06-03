from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_connection
from backend.auth import get_current_user
from backend.models.solicitud import SolicitudCreate, SolicitudResponse
import json


router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


@router.post("")
def crear_solicitud(datos: SolicitudCreate, usuario: dict = Depends(get_current_user)):
    if usuario["rol"] != "cliente":
        raise HTTPException(status_code=403, detail="Solo los clientes pueden solicitar ser administradores")

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id FROM solicitudes_admin WHERE id_usuario = %s AND estado = 'pendiente'",
        (usuario["id"],)
    )
    if cursor.fetchone():
        conexion.close()
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud pendiente")

    horarios_json = json.dumps([h.model_dump() for h in datos.horarios]) if datos.horarios else '[]'

    try:
        cursor.execute(
            """INSERT INTO solicitudes_admin
               (id_usuario, nombre_restaurante, telefono, direccion, descripcion, num_mesas, capacidad_mesas, horarios)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)""",
            (usuario["id"], datos.nombre_restaurante, datos.telefono,
             datos.direccion, datos.descripcion, datos.num_mesas, datos.capacidad_mesas, horarios_json)
        )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Solicitud enviada correctamente, espera la aprobación de un superadmin"}


@router.get("", response_model=list[SolicitudResponse])
def listar_solicitudes(estado: str = None, usuario: dict = Depends(get_current_user)):
    if usuario["rol"] != "superadmin":
        raise HTTPException(status_code=403, detail="Solo los superadmins pueden ver las solicitudes")

    conexion = get_connection()
    cursor = conexion.cursor()

    if estado:
        cursor.execute("""
            SELECT s.id, s.id_usuario, u.nombre, u.correo,
                   s.nombre_restaurante, s.telefono, s.direccion, s.descripcion,
                   s.num_mesas, s.capacidad_mesas, s.horarios, s.estado, s.fecha_solicitud
            FROM solicitudes_admin s
            JOIN usuarios u ON s.id_usuario = u.id
            WHERE s.estado = %s
            ORDER BY s.fecha_solicitud DESC
        """, (estado,))
    else:
        cursor.execute("""
            SELECT s.id, s.id_usuario, u.nombre, u.correo,
                   s.nombre_restaurante, s.telefono, s.direccion, s.descripcion,
                   s.num_mesas, s.capacidad_mesas, s.horarios, s.estado, s.fecha_solicitud
            FROM solicitudes_admin s
            JOIN usuarios u ON s.id_usuario = u.id
            ORDER BY s.fecha_solicitud DESC
        """)

    datos = cursor.fetchall()
    conexion.close()

    return [
        {
            "id": f[0], "id_usuario": f[1], "nombre_usuario": f[2], "correo_usuario": f[3],
            "nombre_restaurante": f[4], "telefono": f[5], "direccion": f[6], "descripcion": f[7],
            "num_mesas": f[8], "capacidad_mesas": f[9],
            "horarios": f[10] if f[10] else [],
            "estado": f[11], "fecha_solicitud": str(f[12])
        }
        for f in datos
    ]


@router.put("/{id_solicitud}/aprobar")
def aprobar_solicitud(id_solicitud: int, usuario: dict = Depends(get_current_user)):
    if usuario["rol"] != "superadmin":
        raise HTTPException(status_code=403, detail="Solo los superadmins pueden aprobar solicitudes")

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id_usuario, nombre_restaurante, telefono, direccion, descripcion, num_mesas, capacidad_mesas, horarios, estado FROM solicitudes_admin WHERE id = %s",
        (id_solicitud,)
    )
    solicitud = cursor.fetchone()

    if solicitud is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if solicitud[8] != "pendiente":
        conexion.close()
        raise HTTPException(status_code=400, detail=f"La solicitud ya fue {solicitud[8]}")

    id_usuario = solicitud[0]
    nombre_rest = solicitud[1]
    telefono = solicitud[2]
    direccion = solicitud[3]
    descripcion = solicitud[4]
    num_mesas = solicitud[5]
    capacidad = solicitud[6]
    horarios = solicitud[7] if solicitud[7] else []

    try:
        cursor.execute("UPDATE usuarios SET rol = 'admin' WHERE id = %s", (id_usuario,))

        cursor.execute(
            "INSERT INTO restaurante (id_usuario, nombre, direccion, telefono, descripcion) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (id_usuario, nombre_rest, direccion, telefono, descripcion)
        )
        id_restaurante = cursor.fetchone()[0]

        for i in range(1, num_mesas + 1):
            cursor.execute(
                "INSERT INTO mesa (id_restaurante, numero_mesa, capacidad) VALUES (%s, %s, %s)",
                (id_restaurante, i, capacidad)
            )

        for h in horarios:
            cursor.execute(
                "INSERT INTO horario (id_restaurante, dia_semana, hora_apertura, hora_cierre) VALUES (%s, %s, %s, %s)",
                (id_restaurante, h["dia"], h["apertura"], h["cierre"])
            )

        cursor.execute(
            "UPDATE solicitudes_admin SET estado = 'aprobada' WHERE id = %s",
            (id_solicitud,)
        )

        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Solicitud aprobada, el usuario ahora es administrador"}


@router.put("/{id_solicitud}/rechazar")
def rechazar_solicitud(id_solicitud: int, usuario: dict = Depends(get_current_user)):
    if usuario["rol"] != "superadmin":
        raise HTTPException(status_code=403, detail="Solo los superadmins pueden rechazar solicitudes")

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("SELECT estado FROM solicitudes_admin WHERE id = %s", (id_solicitud,))
    solicitud = cursor.fetchone()

    if solicitud is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if solicitud[0] != "pendiente":
        conexion.close()
        raise HTTPException(status_code=400, detail=f"La solicitud ya fue {solicitud[0]}")

    try:
        cursor.execute(
            "UPDATE solicitudes_admin SET estado = 'rechazada' WHERE id = %s",
            (id_solicitud,)
        )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Solicitud rechazada"}
