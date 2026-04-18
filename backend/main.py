from fastapi import FastAPI
import psycopg2

app = FastAPI()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="reservibe",
        user="postgres",
        password="1234",
        port="5432"
    )

@app.get("/usuarios")
def obtener_usuarios():
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()

    usuarios = []
    for fila in datos:
        usuarios.append({
            "id": fila[0],
            "nombre": fila[1],
            "correo": fila[2],
            "rol": fila[4],
            "fecha": str(fila[5])
        })

    conexion.close()
    return usuarios
