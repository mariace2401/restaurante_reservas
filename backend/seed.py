from backend.database import get_connection

USUARIOS = [
    (1, "Santiago", "santiago@gmail.com", "$2b$12$FpDS.lt8/6lcxoVmdh/XreGsE5MGjE0fCO3IiCe6H.Ii.0dUA0WDW", "admin"),
    (2, "Admin ReserVibe", "admin@reservibe.com", "$2b$12$sUuuAoZflvJbExN.fhWHb.beQqiXJLkW.OmZ16gRaoc627HvBx5q2", "cliente"),
    (3, "Santiago Aristizabal", "aristizabal7@gmail.com", "$2b$12$EajoM8eLPqJnRo5FE.QqZOIF5MHkp3lExo8XxX9aBSX/aTuvos17K", "cliente"),
    (4, "Mariana", "mari2401@gmail.com", "$2b$12$a0HZSp7BsmSiUWm0ewvpdOyRjuyttRwEFeH.pOc.e/g1OZAv0dJCa", "cliente"),
    (5, "Juan Felipe Londoño", "Juanfelipelondonomarin@gmail.com", "$2b$12$8QLG7Y3/XE/lytiFTAAR6.MOMwgWWnWXYmuelmkvwSizGXXZv5Un2", "cliente"),
]

RESTAURANTES = [
    (1, 1, "Crepes & Waffles", "Centro Comercial Unicentro, Pereira", "3101111111", "Cocina internacional, crepes dulces y salados"),
    (2, 1, "Frisby", "Carrera 8 #18-32, Pereira", "3102222222", "Pollo frito estilo colombiano"),
    (3, 1, "Salchipaisa", "Calle 19 #6-10, Pereira", "3103333333", "Comida típica paisa, salchipapas y más"),
    (4, 1, "Dragón de Oro", "Carrera 10 #15-40, Pereira", "3104444444", "Restaurante de comida china, especialidad en arroz"),
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

RESERVAS = [
    (1, 3, 5, "2026-04-30", "19:56", 2, "cancelada"),
    (2, 3, 10, "2026-04-30", "16:30", 4, "pendiente"),
    (3, 4, 5, "2026-05-01", "15:58", 2, "pendiente"),
    (4, 3, 1, "2026-04-05", "16:00", 2, "pendiente"),
    (5, 3, 15, "2026-05-04", "12:30", 1, "cancelada"),
    (6, 3, 15, "2026-05-04", "12:30", 5, "cancelada"),
    (7, 3, 15, "2026-05-04", "12:30", 5, "pendiente"),
    (8, 3, 6, "2026-05-04", "12:29", 4, "pendiente"),
    (9, 3, 8, "2026-05-05", "23:50", 5, "pendiente"),
    (10, 3, 6, "2026-05-04", "12:29", 4, "pendiente"),
    (11, 3, 1, "2026-05-04", "14:25", 2, "pendiente"),
    (12, 3, 10, "2026-05-08", "16:30", 4, "pendiente"),
    (13, 5, 15, "2026-10-30", "14:00", 5, "pendiente"),
]


def seed_data():
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM restaurante")
    if cursor.fetchone()[0] > 0:
        conexion.close()
        print("ℹ️  La base de datos ya tiene datos semilla")
        return

    for u in USUARIOS:
        cursor.execute(
            "INSERT INTO usuarios (id, nombre, correo, password, rol) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            u,
        )
    for r in RESTAURANTES:
        cursor.execute(
            "INSERT INTO restaurante (id, id_usuario, nombre, direccion, telefono, descripcion) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            r,
        )
    for h in HORARIOS:
        cursor.execute(
            "INSERT INTO horario (id, id_restaurante, dia_semana, hora_apertura, hora_cierre) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            h,
        )
    for m in MESAS:
        cursor.execute(
            "INSERT INTO mesa (id, id_restaurante, numero_mesa, capacidad) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            m,
        )
    for rv in RESERVAS:
        cursor.execute(
            "INSERT INTO reservas (id, usuario_id, id_mesa, fecha, hora, personas, estado) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            rv,
        )

    cursor.execute("SELECT setval('usuarios_id_seq', (SELECT MAX(id) FROM usuarios))")
    cursor.execute("SELECT setval('restaurante_id_seq', (SELECT MAX(id) FROM restaurante))")
    cursor.execute("SELECT setval('horario_id_seq', (SELECT MAX(id) FROM horario))")
    cursor.execute("SELECT setval('mesa_id_seq', (SELECT MAX(id) FROM mesa))")
    cursor.execute("SELECT setval('reservas_id_seq', (SELECT MAX(id) FROM reservas))")

    conexion.commit()
    conexion.close()
    print("✅ Datos semilla insertados correctamente")


if __name__ == "__main__":
    seed_data()
