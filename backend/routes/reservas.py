from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_connection
from backend.auth import get_current_user
from backend.models.reserva import ReservaCreate


router = APIRouter(prefix="/reservas", tags=["reservas"])


@router.post("")
def crear_reserva(reserva: ReservaCreate, usuario: dict = Depends(get_current_user)):
    conexion = get_connection()
    cursor = conexion.cursor()

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


@router.get("/mis-reservas")
def mis_reservas(usuario: dict = Depends(get_current_user)):
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


@router.delete("/{id_reserva}")
def cancelar_reserva(id_reserva: int, usuario: dict = Depends(get_current_user)):
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