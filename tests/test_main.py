import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

# ================================
# DATOS DE PRUEBA
# ================================
USUARIO_TEST = {
    "nombre": "Test User",
    "correo": "test@reservibe.com",
    "password": "test1234"
}

USUARIO_LOGIN = {
    "correo": "test@reservibe.com",
    "password": "test1234"
}


# ================================
# HELPER — token válido
# ================================
def get_token():
    response = client.post("/auth/login", json=USUARIO_LOGIN)
    return response.json().get("access_token")


# ================================
# TESTS — REGISTRO
# ================================

def test_registro_exitoso():
    """Registro con datos válidos debe retornar 200"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.auth.get_connection", return_value=mock_conn):
        response = client.post("/auth/registro", json=USUARIO_TEST)

    assert response.status_code == 200
    assert "mensaje" in response.json()


def test_registro_correo_duplicado():
    """Registro con correo ya existente debe retornar 400"""
    import psycopg2
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = psycopg2.errors.UniqueViolation()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.auth.get_connection", return_value=mock_conn):
        response = client.post("/auth/registro", json=USUARIO_TEST)

    assert response.status_code == 400
    assert "correo" in response.json()["detail"].lower() or "existe" in response.json()["detail"].lower()


# ================================
# TESTS — LOGIN
# ================================

def test_login_exitoso():
    """Login con credenciales correctas debe retornar token"""
    import bcrypt
    hashed = bcrypt.hashpw(b"test1234", bcrypt.gensalt()).decode("utf-8")

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Test User", "test@reservibe.com", hashed, "cliente")
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.auth.get_connection", return_value=mock_conn):
        response = client.post("/auth/login", json=USUARIO_LOGIN)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["access_token"] is not None


def test_login_usuario_no_existe():
    """Login con correo no registrado debe retornar 404"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.auth.get_connection", return_value=mock_conn):
        response = client.post("/auth/login", json=USUARIO_LOGIN)

    assert response.status_code == 404


def test_login_password_incorrecta():
    """Login con contraseña incorrecta debe retornar 401"""
    import bcrypt
    hashed = bcrypt.hashpw(b"otrapassword", bcrypt.gensalt()).decode("utf-8")

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Test User", "test@reservibe.com", hashed, "cliente")
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.auth.get_connection", return_value=mock_conn):
        response = client.post("/auth/login", json=USUARIO_LOGIN)

    assert response.status_code == 401


# ================================
# TESTS — RESTAURANTES
# ================================

def test_listar_restaurantes():
    """GET /restaurantes debe retornar lista"""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "Frisby", "Carrera 8 #18-32", "3102222222", "Pollo frito", "Admin"),
        (2, "Crepes & Waffles", "Unicentro", "3101111111", "Cocina internacional", "Admin")
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.restaurantes.get_connection", return_value=mock_conn):
        response = client.get("/restaurantes")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2


def test_detalle_restaurante_no_existe():
    """GET /restaurantes/999 debe retornar 404"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.restaurantes.get_connection", return_value=mock_conn):
        response = client.get("/restaurantes/999")

    assert response.status_code == 404


# ================================
# TESTS — RESERVAS
# ================================

def test_crear_reserva_sin_token():
    """POST /reservas sin token debe retornar 401"""
    response = client.post("/reservas", json={
        "id_mesa": 1,
        "fecha": "2026-06-01",
        "hora": "19:00",
        "personas": 2
    })
    assert response.status_code == 401


def test_crear_reserva_mesa_no_existe():
    """POST /reservas con mesa inexistente debe retornar 404"""
    import bcrypt
    from backend.auth import crear_token
    token = crear_token({"id": 1, "correo": "test@reservibe.com", "rol": "cliente"})

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.reservas.get_connection", return_value=mock_conn):
        response = client.post(
            "/reservas",
            json={"id_mesa": 999, "fecha": "2026-06-01", "hora": "19:00", "personas": 2},
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 404


def test_mis_reservas_sin_token():
    """GET /reservas/mis-reservas sin token debe retornar 401"""
    response = client.get("/reservas/mis-reservas")
    assert response.status_code == 401


def test_cancelar_reserva_sin_token():
    """DELETE /reservas/1 sin token debe retornar 401"""
    response = client.delete("/reservas/1")
    assert response.status_code == 401


def test_cancelar_reserva_no_existe():
    """DELETE /reservas/999 debe retornar 404"""
    from backend.auth import crear_token
    token = crear_token({"id": 1, "correo": "test@reservibe.com", "rol": "cliente"})

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("backend.routes.reservas.get_connection", return_value=mock_conn):
        response = client.delete(
            "/reservas/999",
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 404