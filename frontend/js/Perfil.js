const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://restaurante-reservas-g9hl.onrender.com';

const rol = localStorage.getItem('rv_rol');
if (rol === 'cliente') document.getElementById('nav-solicitar-admin').style.display = '';
if (rol === 'admin') document.getElementById('nav-mi-restaurante').style.display = '';
if (rol === 'superadmin') document.getElementById('nav-solicitudes').style.display = '';

function logout() {
  localStorage.removeItem('rv_token');
  localStorage.removeItem('rv_rol');
  window.location.href = '/';
}

function showMsg(type, text) {
  const el = document.getElementById('msg');
  el.className = 'msg ' + type;
  el.textContent = text;
}

async function cargarPerfil() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = '/'; return; }

  try {
    const r = await fetch(API + '/usuarios/me', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const data = await r.json();
    document.getElementById('nombre').value = data.nombre;
    document.getElementById('correo').value = data.correo;
    document.getElementById('rol').value = data.rol;
  } catch {
    showMsg('err', 'Error al cargar perfil');
  }
}

async function guardarPerfil() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = '/'; return; }

  const nombre = document.getElementById('nombre').value.trim();
  const password = document.getElementById('password').value;

  if (!nombre) {
    showMsg('err', 'El nombre no puede estar vacío');
    return;
  }

  const body = { nombre };
  if (password) {
    if (password.length < 8) {
      showMsg('err', 'La contraseña debe tener al menos 8 caracteres');
      return;
    }
    body.password = password;
  }

  try {
    const r = await fetch(API + '/usuarios/me', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify(body)
    });
    const d = await r.json();
    if (r.ok) {
      showMsg('ok', 'Perfil actualizado correctamente');
      document.getElementById('password').value = '';
    } else {
      showMsg('err', d.detail || 'Error al actualizar');
    }
  } catch {
    showMsg('err', 'No se pudo conectar al servidor');
  }
}

cargarPerfil();
