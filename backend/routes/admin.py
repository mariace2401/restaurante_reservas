from fastapi import APIRouter, Depends, HTTPException, Query
from backend.database import get_connection
from backend.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])


def verificar_admin(usuario: dict):
    if usuario["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden acceder")


def listar_restaurantes_admin(cursor, id_usuario: int):
    cursor.execute(
        "SELECT id, nombre, direccion, telefono, descripcion FROM restaurante WHERE id_usuario = %s ORDER BY nombre",
        (id_usuario,)
    )
    return cursor.fetchall()


def obtener_restaurante_admin_por_id(cursor, id_restaurante: int, id_usuario: int):
    cursor.execute(
        "SELECT id, nombre, direccion, telefono, descripcion FROM restaurante WHERE id = %s AND id_usuario = %s",
        (id_restaurante, id_usuario)
    )
    return cursor.fetchone()


def resolver_restaurante(cursor, id_usuario: int, restaurante_id: Optional[int] = None):
    if restaurante_id is not None:
        rest = obtener_restaurante_admin_por_id(cursor, restaurante_id, id_usuario)
        if rest is None:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado o no te pertenece")
        return rest
    todos = listar_restaurantes_admin(cursor, id_usuario)
    if not todos:
        raise HTTPException(status_code=404, detail="No tienes restaurantes asignados")
    if len(todos) > 1:
        raise HTTPException(
            status_code=400,
            detail=f"Tienes {len(todos)} restaurantes. Especifica ?restaurante_id= con el id del restaurante"
        )
    return todos[0]


@router.get("/mis-restaurantes")
def mis_restaurantes(usuario: dict = Depends(get_current_user)):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()
    restaurantes = listar_restaurantes_admin(cursor, usuario["id"])
    conexion.close()

    return [
        {"id": r[0], "nombre": r[1], "direccion": r[2], "telefono": r[3], "descripcion": r[4]}
        for r in restaurantes
    ]


@router.put("/mi-restaurante")
def actualizar_restaurante(
    datos: dict,
    restaurante_id: Optional[int] = Query(None),
    usuario: dict = Depends(get_current_user)
):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = resolver_restaurante(cursor, usuario["id"], restaurante_id)

    campos = {}
    for key in ("nombre", "direccion", "telefono", "descripcion"):
        if key in datos:
            campos[key] = datos[key]

    if not campos:
        conexion.close()
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    sets = ", ".join(f"{k} = %s" for k in campos)
    params = list(campos.values()) + [restaurante[0]]

    try:
        cursor.execute(f"UPDATE restaurante SET {sets} WHERE id = %s", params)
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Restaurante actualizado correctamente"}


@router.put("/mi-restaurante/horarios")
def actualizar_horarios(
    horarios: list[dict],
    restaurante_id: Optional[int] = Query(None),
    usuario: dict = Depends(get_current_user)
):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = resolver_restaurante(cursor, usuario["id"], restaurante_id)
    id_rest = restaurante[0]

    dias_validos = {"lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"}

    for h in horarios:
        if h.get("dia") not in dias_validos:
            conexion.close()
            raise HTTPException(status_code=400, detail=f"Día inválido: {h.get('dia')}")

    try:
        cursor.execute("DELETE FROM horario WHERE id_restaurante = %s", (id_rest,))
        for h in horarios:
            cursor.execute(
                "INSERT INTO horario (id_restaurante, dia_semana, hora_apertura, hora_cierre) VALUES (%s, %s, %s, %s)",
                (id_rest, h["dia"], h["apertura"], h["cierre"])
            )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Horarios actualizados correctamente"}


@router.post("/mi-restaurante/mesas")
def agregar_mesa(
    datos: dict,
    restaurante_id: Optional[int] = Query(None),
    usuario: dict = Depends(get_current_user)
):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = resolver_restaurante(cursor, usuario["id"], restaurante_id)

    numero = datos.get("numero_mesa")
    capacidad = datos.get("capacidad")
    if not numero or not capacidad:
        conexion.close()
        raise HTTPException(status_code=400, detail="numero_mesa y capacidad son requeridos")

    try:
        cursor.execute(
            "INSERT INTO mesa (id_restaurante, numero_mesa, capacidad) VALUES (%s, %s, %s) RETURNING id",
            (restaurante[0], numero, capacidad)
        )
        id_mesa = cursor.fetchone()[0]
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Mesa agregada", "id_mesa": id_mesa}


@router.put("/mi-restaurante/mesas/{id_mesa}")
def actualizar_mesa(
    id_mesa: int,
    datos: dict,
    restaurante_id: Optional[int] = Query(None),
    usuario: dict = Depends(get_current_user)
):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = resolver_restaurante(cursor, usuario["id"], restaurante_id)

    cursor.execute(
        "SELECT id FROM mesa WHERE id = %s AND id_restaurante = %s",
        (id_mesa, restaurante[0])
    )
    if cursor.fetchone() is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Mesa no encontrada en tu restaurante")

    updates = []
    params = []
    for key in ("capacidad", "numero_mesa", "disponible"):
        if key in datos:
            updates.append(f"{key} = %s")
            params.append(datos[key])

    if not updates:
        conexion.close()
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    params.append(id_mesa)

    try:
        cursor.execute(f"UPDATE mesa SET {', '.join(updates)} WHERE id = %s", params)
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Mesa actualizada correctamente"}


@router.delete("/mi-restaurante/mesas/{id_mesa}")
def eliminar_mesa(
    id_mesa: int,
    restaurante_id: Optional[int] = Query(None),
    usuario: dict = Depends(get_current_user)
):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = resolver_restaurante(cursor, usuario["id"], restaurante_id)

    cursor.execute(
        "SELECT id FROM mesa WHERE id = %s AND id_restaurante = %s",
        (id_mesa, restaurante[0])
    )
    if cursor.fetchone() is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Mesa no encontrada en tu restaurante")

    try:
        cursor.execute("DELETE FROM mesa WHERE id = %s", (id_mesa,))
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Mesa eliminada correctamente"}


@router.put("/mi-restaurante/reservas/{id_reserva}/confirmar")
def confirmar_reserva(
    id_reserva: int,
    restaurante_id: Optional[int] = Query(None),
    usuario: dict = Depends(get_current_user)
):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = resolver_restaurante(cursor, usuario["id"], restaurante_id)

    cursor.execute("""
        SELECT r.estado FROM reservas r
        JOIN mesa m ON r.id_mesa = m.id
        WHERE r.id = %s AND m.id_restaurante = %s
    """, (id_reserva, restaurante[0]))
    reserva = cursor.fetchone()

    if reserva is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Reserva no encontrada en tu restaurante")

    if reserva[0] != "pendiente":
        conexion.close()
        raise HTTPException(status_code=400, detail=f"La reserva ya está {reserva[0]}")

    try:
        cursor.execute("UPDATE reservas SET estado = 'confirmada' WHERE id = %s", (id_reserva,))
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Reserva confirmada correctamente"}


@router.get("/mi-restaurante/reservas")
def listar_reservas_restaurante(
    fecha: Optional[str] = None,
    estado: Optional[str] = None,
    restaurante_id: Optional[int] = Query(None),
    usuario: dict = Depends(get_current_user)
):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = resolver_restaurante(cursor, usuario["id"], restaurante_id)

    query = """
        SELECT r.id, r.fecha, r.hora, r.personas, r.estado,
               u.nombre AS cliente, u.correo AS correo_cliente,
               m.numero_mesa
        FROM reservas r
        JOIN mesa m ON r.id_mesa = m.id
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE m.id_restaurante = %s
    """
    params = [restaurante[0]]

    if fecha:
        query += " AND r.fecha = %s"
        params.append(fecha)
    if estado:
        query += " AND r.estado = %s"
        params.append(estado)

    query += " ORDER BY r.fecha DESC, r.hora DESC"

    cursor.execute(query, params)
    datos = cursor.fetchall()
    conexion.close()

    return [
        {
            "id": f[0],
            "fecha": str(f[1]),
            "hora": str(f[2]),
            "personas": f[3],
            "estado": f[4],
            "cliente": f[5],
            "correo_cliente": f[6],
            "mesa": f[7]
        }
        for f in datos
    ]


@router.get("/mi-restaurante/{id_restaurante}")
def detalle_restaurante(id_restaurante: int, usuario: dict = Depends(get_current_user)):
    verificar_admin(usuario)

    conexion = get_connection()
    cursor = conexion.cursor()

    restaurante = obtener_restaurante_admin_por_id(cursor, id_restaurante, usuario["id"])
    if restaurante is None:
        conexion.close()
        raise HTTPException(status_code=404, detail="Restaurante no encontrado o no te pertenece")

    id_rest = restaurante[0]

    cursor.execute("""
        SELECT dia_semana, hora_apertura, hora_cierre
        FROM horario
        WHERE id_restaurante = %s
        ORDER BY CASE dia_semana
            WHEN 'lunes' THEN 1 WHEN 'martes' THEN 2 WHEN 'miércoles' THEN 3
            WHEN 'jueves' THEN 4 WHEN 'viernes' THEN 5
            WHEN 'sábado' THEN 6 WHEN 'domingo' THEN 7
        END
    """, (id_rest,))
    horarios = cursor.fetchall()

    cursor.execute("""
        SELECT id, numero_mesa, capacidad, disponible
        FROM mesa
        WHERE id_restaurante = %s
        ORDER BY numero_mesa
    """, (id_rest,))
    mesas = cursor.fetchall()

    conexion.close()

    return {
        "id": restaurante[0],
        "nombre": restaurante[1],
        "direccion": restaurante[2],
        "telefono": restaurante[3],
        "descripcion": restaurante[4],
        "horarios": [
            {"dia": h[0], "apertura": str(h[1]), "cierre": str(h[2])}
            for h in horarios
        ],
        "mesas": [
            {"id": m[0], "numero": m[1], "capacidad": m[2], "disponible": m[3]}
            for m in mesas
        ]
    }
