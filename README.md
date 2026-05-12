# 🍽️ ReserVibe - Sistema de Reservas de Restaurantes

Plataforma web moderna para la gestión y reserva de mesas en restaurantes, desarrollada con **FastAPI**, **PostgreSQL** y **Vanilla JavaScript**.

## 📋 Características

- **Autenticación segura** - Registro e inicio de sesión con JWT y bcrypt
- **Catálogo de restaurantes** - Explora restaurantes con horarios y mesas disponibles
- **Reservas en tiempo real** - Crea reservas validando disponibilidad y capacidad
- **Gestión de reservas** - Visualiza y cancela tus reservas fácilmente
- **Roles de usuario** - Diferenciación entre clientes y administradores
- **Interfaz moderna** - Tema oscuro responsive con animaciones suaves
- **Documentación automática** - API docs interactiva con Swagger UI

## 🛠️ Tecnologías

### Backend
- **Python 3.12** - Lenguaje principal
- **FastAPI 0.136** - Framework web moderno y rápido
- **Uvicorn** - Servidor ASGI
- **PostgreSQL 15** - Base de datos relacional
- **Pydantic v2** - Validación de datos
- **python-jose** - Manejo de JWT
- **bcrypt** - Hash de contraseñas

### Frontend
- **HTML5 / CSS3** - Estructura y estilos personalizados
- **JavaScript (Vanilla)** - Lógica de cliente sin frameworks
- **Google Fonts** - DM Serif Display & DM Sans

### Infraestructura
- **Docker + docker-compose** - PostgreSQL y pgAdmin4
- **Git** - Control de versiones

## 📁 Estructura del Proyecto

```
restaurante_reservas/
├── main.py                    # Entry point de FastAPI
├── backend/
│   ├── auth.py               # JWT y autenticación
│   ├── database.py           # Conexión a PostgreSQL
│   ├── models/               # Esquemas Pydantic
│   │   ├── usuario.py
│   │   ├── restaurante.py
│   │   └── reserva.py
│   └── routes/               # Endpoints API
│       ├── auth.py
│       ├── reservas.py
│       └── restaurantes.py
├── frontend/
│   ├── index.html            # Login / Registro
│   ├── Restaurantes.html     # Lista de restaurantes
│   ├── Reservar.html         # Formulario de reserva
│   ├── Misreservas.html      # Mis reservas
│   ├── css/style.css         # Estilos tema oscuro
│   └── js/                   # Lógica del cliente
│       ├── auth.js
│       ├── Restaurantes.js
│       ├── Reservar.js
│       └── Misreservas.js
├── docker-compose.yml        # Contenedores PostgreSQL + pgAdmin
├── requirements.txt          # Dependencias Python
└── .env                      # Variables de entorno
```

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.12+
- Docker y docker-compose
- Git

### Pasos

1. **Clonar el repositorio**
```bash
git clone <repo-url>
cd restaurante_reservas
```

2. **Crear y activar entorno virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Levantar base de datos con Docker**
```bash
docker-compose up -d
```

5. **Configurar variables de entorno**
Edita el archivo `.env` con tus credenciales:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reservibe
DB_USER=postgres
DB_PASSWORD=tu_password
SECRET_KEY=tu_clave_secreta_segura
```

6. **Crear las tablas en la base de datos**
Accede a pgAdmin en `http://localhost:5050` (admin@admin.com / 1234) y ejecuta el SQL necesario para crear las tablas `usuarios`, `restaurante`, `mesa`, `reservas`, `horario`.

7. **Ejecutar la aplicación**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

8. **Abrir en el navegador**
- **Frontend:** http://127.0.0.1:8000
- **API Docs:** http://127.0.0.1:8000/docs
- **pgAdmin:** http://localhost:5050

## 📡 API Endpoints

### Autenticación `/auth`
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/registro` | Registrar nuevo usuario |
| POST | `/auth/login` | Iniciar sesión (retorna JWT) |

### Restaurantes `/restaurantes`
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/restaurantes` | Listar todos los restaurantes |
| GET | `/restaurantes/{id}` | Detalles con horarios y mesas |

### Reservas `/reservas`
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/reservas` | ✅ | Crear reserva |
| GET | `/reservas/mis-reservas` | ✅ | Mis reservas |
| DELETE | `/reservas/{id}` | ✅ | Cancelar reserva |

## 🗄️ Esquema de Base de Datos

| Tabla | Descripción |
|-------|-------------|
| `usuarios` | Datos de usuarios y roles |
| `restaurante` | Información de restaurantes |
| `mesa` | Mesas con capacidad y disponibilidad |
| `reservas` | Registro de reservas |
| `horario` | Horarios de apertura por día |

## ⚙️ Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reservibe
DB_USER=postgres
DB_PASSWORD=password
SECRET_KEY=clave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado como parte del curso de **Entornos de Desarrollo de Software**.

---

⭐ Si te gusta el proyecto, dale una estrella en GitHub!
