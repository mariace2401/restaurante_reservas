from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_connection
from backend.auth import get_current_user
from backend.models.usuario import UsuarioUpdate, UsuarioResponse
import bcrypt

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioResponse)
def perfil_usuario(usuario: dict = Depends(get_current_user)):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, correo, rol, fecha FROM usuarios WHERE id = %s",
        (usuario["id"],)
    )
    data = cursor.fetchone()
    conexion.close()

    if data is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": data[0],
        "nombre": data[1],
        "correo": data[2],
        "rol": data[3],
        "fecha": str(data[4]) if data[4] else None
    }


@router.put("/me")
def actualizar_perfil(datos: UsuarioUpdate, usuario: dict = Depends(get_current_user)):
    conexion = get_connection()
    cursor = conexion.cursor()

    updates = []
    params = []

    if datos.nombre is not None:
        updates.append("nombre = %s")
        params.append(datos.nombre)

    if datos.password is not None:
        hashed = bcrypt.hashpw(datos.password.encode('utf-8'), bcrypt.gensalt())
        updates.append("password = %s")
        params.append(hashed.decode('utf-8'))

    if not updates:
        conexion.close()
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    params.append(usuario["id"])

    try:
        cursor.execute(
            f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s",
            params
        )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conexion.close()

    return {"mensaje": "Perfil actualizado correctamente"}
