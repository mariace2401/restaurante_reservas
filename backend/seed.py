from backend.database import get_connection

USUARIOS = [
    ("Santiago Aristizabal", "aristisantiago7@gmail.com", "$2b$12$VYA6faCVQr2zMnsDIllhO.7DPy8pGJlB68jNS9N9W5AWVkz.PxqfO", "superadmin"),
    ("Mariana Acevedo", "mariace2401@gmail.com", "$2b$12$RsHAmpP0ZEsn8TdYEa2nx.UrKL.N6pgRgmuogNt/5vlU7TvtUcnmy", "admin"),
]

RESTAURANTES = [
    (1, 2, "Crepes & Waffles", "Centro Comercial Unicentro, Pereira", "3101111111", "Cocina internacional, crepes dulces y salados"),
    (2, 2, "Frisby", "Carrera 8 #18-32, Pereira", "3102222222", "Pollo frito estilo colombiano"),
    (3, 2, "Salchipaisa", "Calle 19 #6-10, Pereira", "3103333333", "Comida típica paisa, salchipapas y más"),
    (4, 2, "Dragón de Oro", "Carrera 10 #15-40, Pereira", "3104444444", "Restaurante de comida china, especialidad en arroz"),
]

HORARIOS = [
    (1, 1, "lunes", "10:00", "22:00"), (2, 1, "martes", "10:00", "22:00"),
    (3, 1, "miércoles", "10:00", "22:00"), (4, 1, "jueves", "10:00", "22:00"),
    (5, 1, "viernes", "10:00", "23:00"), (6, 1, "sábado", "10:00", "23:00"),
    (7, 1, "domingo", "11:00", "21:00"),
    (8, 2, "lunes", "09:00", "21:00"), (9, 2, "martes", "09:00", "21:00"),
    (10, 2, "miércoles", "09:00", "21:00"), (11, 2, "jueves", "09:00", "21:00"),
    (12, 2, "viernes", "09:00", "22:00"), (13, 2, "sábado", "09:00", "22:00"),
    (14, 2, "domingo", "10:00", "21:00"),
    (15, 3, "lunes", "08:00", "20:00"), (16, 3, "martes", "08:00", "20:00"),
    (17, 3, "miércoles", "08:00", "20:00"), (18, 3, "jueves", "08:00", "20:00"),
    (19, 3, "viernes", "08:00", "21:00"), (20, 3, "sábado", "08:00", "21:00"),
    (21, 4, "lunes", "11:00", "22:00"), (22, 4, "martes", "11:00", "22:00"),
    (23, 4, "miércoles", "11:00", "22:00"), (24, 4, "jueves", "11:00", "22:00"),
    (25, 4, "viernes", "11:00", "23:00"), (26, 4, "sábado", "11:00", "23:00"),
    (27, 4, "domingo", "12:00", "21:00"),
]

MESAS = [
    (1, 1, 1, 2), (2, 1, 2, 4), (3, 1, 3, 4), (4, 1, 4, 6),
    (5, 2, 1, 2), (6, 2, 2, 4), (7, 2, 3, 4), (8, 2, 4, 8),
    (9, 3, 1, 2), (10, 3, 2, 4), (11, 3, 3, 6),
    (12, 4, 1, 2), (13, 4, 2, 4), (14, 4, 3, 4), (15, 4, 4, 6),
]

RESERVAS = []


def seed_data():
    conexion = get_connection()
    cursor = conexion.cursor()

    # --- Always insert seed users by email (never skip) ---
    for nombre, correo, password, rol in USUARIOS:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, password, rol) "
            "VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (correo) DO NOTHING",
            (nombre, correo, password, rol),
        )

    # --- Look up actual IDs for admin users ---
    admin_id = None
    for _, correo, _, rol in USUARIOS:
        cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
        row = cursor.fetchone()
        if row and rol == "admin":
            admin_id = row[0]

    # --- Restaurants: always point to the real admin ID ---
    for r_id, _, nombre, direccion, telefono, descripcion in RESTAURANTES:
        cursor.execute(
            "INSERT INTO restaurante (id, id_usuario, nombre, direccion, telefono, descripcion) "
            "VALUES (%s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET id_usuario = EXCLUDED.id_usuario",
            (r_id, admin_id, nombre, direccion, telefono, descripcion),
        )

    for h in HORARIOS:
        cursor.execute(
            "INSERT INTO horario (id, id_restaurante, dia_semana, hora_apertura, hora_cierre) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON CONFLICT (id) DO NOTHING",
            h,
        )
    for m in MESAS:
        cursor.execute(
            "INSERT INTO mesa (id, id_restaurante, numero_mesa, capacidad) "
            "VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (id) DO NOTHING",
            m,
        )
    for rv in RESERVAS:
        cursor.execute(
            "INSERT INTO reservas (id, usuario_id, id_mesa, fecha, hora, personas, estado) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (id) DO NOTHING",
            rv,
        )

    cursor.execute("SELECT setval('usuarios_id_seq', (SELECT MAX(id) FROM usuarios))")
    cursor.execute("SELECT setval('restaurante_id_seq', (SELECT MAX(id) FROM restaurante))")
    cursor.execute("SELECT setval('horario_id_seq', (SELECT MAX(id) FROM horario))")
    cursor.execute("SELECT setval('mesa_id_seq', (SELECT MAX(id) FROM mesa))")
    cursor.execute("SELECT setval('reservas_id_seq', (SELECT MAX(id) FROM reservas))")
    try:
        cursor.execute("SELECT setval('solicitudes_admin_id_seq', (SELECT MAX(id) FROM solicitudes_admin))")
    except:
        pass

    conexion.commit()
    conexion.close()
    print("✅ Datos semilla insertados/actualizados correctamente")


if __name__ == "__main__":
    seed_data()
