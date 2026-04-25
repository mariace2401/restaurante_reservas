from fastapi import APIRouter, HTTPException
from backend.database import get_connection
from backend.models.restaurante import Restaurante_listResponse


router = APIRouter(prefix="/restaurantes", tags=["restaurantes"])


@router.get("", response_model=list[Restaurante_listResponse])
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


@router.get("/{id_restaurante}")
def detalle_restaurante(id_restaurante: int):
    conexion = get_connection()
    cursor = conexion.cursor()

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