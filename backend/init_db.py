from backend.database import get_connection


def init_db():
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id       SERIAL PRIMARY KEY,
            nombre   VARCHAR(100) NOT NULL,
            correo   VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            rol      VARCHAR(20) NOT NULL DEFAULT 'cliente',
            fecha    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurante (
            id          SERIAL PRIMARY KEY,
            id_usuario  INTEGER NOT NULL REFERENCES usuarios(id),
            nombre      VARCHAR(120) NOT NULL,
            direccion   VARCHAR(255) NOT NULL,
            telefono    VARCHAR(20),
            descripcion TEXT
        );
    """)

    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE dia_semana_enum AS ENUM (
                'lunes','martes','miércoles','jueves','viernes','sábado','domingo'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS horario (
            id              SERIAL PRIMARY KEY,
            id_restaurante  INTEGER NOT NULL REFERENCES restaurante(id) ON DELETE CASCADE,
            dia_semana      dia_semana_enum NOT NULL,
            hora_apertura   TIME NOT NULL,
            hora_cierre     TIME NOT NULL,
            UNIQUE (id_restaurante, dia_semana)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesa (
            id              SERIAL PRIMARY KEY,
            id_restaurante  INTEGER NOT NULL REFERENCES restaurante(id) ON DELETE CASCADE,
            numero_mesa     INTEGER NOT NULL,
            capacidad       INTEGER NOT NULL CHECK (capacidad > 0),
            disponible      BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (id_restaurante, numero_mesa)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id          SERIAL PRIMARY KEY,
            usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
            id_mesa     INTEGER REFERENCES mesa(id),
            fecha       DATE NOT NULL,
            hora        TIME NOT NULL,
            personas    INTEGER NOT NULL,
            estado      VARCHAR(20) DEFAULT 'pendiente'
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_admin (
            id                 SERIAL PRIMARY KEY,
            id_usuario         INTEGER NOT NULL REFERENCES usuarios(id),
            nombre_restaurante VARCHAR(120) NOT NULL,
            telefono           VARCHAR(20),
            direccion          VARCHAR(255) NOT NULL,
            descripcion        TEXT,
            num_mesas          INTEGER NOT NULL,
            capacidad_mesas    INTEGER NOT NULL,
            estado             VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            fecha_solicitud    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        ALTER TABLE solicitudes_admin
        ADD COLUMN IF NOT EXISTS horarios JSONB DEFAULT '[]'::jsonb
    """)

    conexion.commit()
    conexion.close()
    print("✅ Base de datos inicializada correctamente")