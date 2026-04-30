const API = "http://127.0.0.1:8000";

function switchTab(t) {
  document.getElementById('panel-login').classList.toggle('active', t === 'login');
  document.getElementById('panel-registro').classList.toggle('active', t === 'registro');
  document.getElementById('tab-login').classList.toggle('active', t === 'login');
  document.getElementById('tab-registro').classList.toggle('active', t === 'registro');
}

function showMsg(id, type, text) {
  const el = document.getElementById(id);
  el.className = 'msg ' + type;
  el.textContent = text;
}

async function doLogin() {
  const correo   = document.getElementById('login-correo').value.trim();
  const password = document.getElementById('login-pass').value;
  if (!correo || !password) { showMsg('login-msg', 'err', 'Completa todos los campos'); return; }
  try {
    const r = await fetch(API + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, password })
    });
    const d = await r.json();
    if (d.access_token) {
      localStorage.setItem('rv_token', d.access_token);
      localStorage.setItem('rv_rol', d.rol);
      showMsg('login-msg', 'ok', '¡Bienvenido! Redirigiendo...');
      setTimeout(() => window.location.href = '/restaurantes-page', 1200);
    } else {
      showMsg('login-msg', 'err', d.detail || 'Credenciales incorrectas');
    }
  } catch { showMsg('login-msg', 'err', 'No se pudo conectar al servidor'); }
}

async function doRegistro() {
  const nombre   = document.getElementById('reg-nombre').value.trim();
  const correo   = document.getElementById('reg-correo').value.trim();
  const password = document.getElementById('reg-pass').value;
  if (!nombre || !correo || !password) { showMsg('reg-msg', 'err', 'Completa todos los campos'); return; }
  if (password.length < 8) { showMsg('reg-msg', 'err', 'La contraseña debe tener al menos 8 caracteres'); return; }
  try {
    const r = await fetch(API + '/auth/registro', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, correo, password })
    });
    const d = await r.json();
    if (r.ok) {
      showMsg('reg-msg', 'ok', '¡Cuenta creada! Ahora inicia sesión.');
      setTimeout(() => switchTab('login'), 1500);
    } else {
      showMsg('reg-msg', 'err', d.detail || 'Error al registrar');
    }
  } catch { showMsg('reg-msg', 'err', 'No se pudo conectar al servidor'); }
}