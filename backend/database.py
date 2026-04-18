import psycopg2

try:
    conexion = psycopg2.connect(
        host="localhost",
        database="reservibe",
        user="postgres",
        password="1234",
        port="5432"
    )

    cursor=conexion.cursor()

    print("Conexión exitosa a la base de datos")


except Exception as e:
    print("Error:", e)
