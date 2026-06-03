const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://restaurante-reservas-g9hl.onrender.com';

const DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];

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

function renderHorarios() {
  const container = document.getElementById('horarios-container');
  container.innerHTML = DIAS.map(d => `
    <div class="row" style="margin-bottom:.5rem;align-items:center">
      <span style="flex:0 0 90px;text-transform:capitalize">${d}</span>
      <input type="time" class="horario-apertura" data-dia="${d}" style="flex:1"/>
      <span style="margin:0 .5rem">a</span>
      <input type="time" class="horario-cierre" data-dia="${d}" style="flex:1"/>
    </div>
  `).join('');
}

async function enviarSolicitud() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = '/'; return; }

  const nombre_restaurante = document.getElementById('nombre_restaurante').value.trim();
  const telefono = document.getElementById('telefono').value.trim();
  const direccion = document.getElementById('direccion').value.trim();
  const descripcion = document.getElementById('descripcion').value.trim();
  const num_mesas = parseInt(document.getElementById('num_mesas').value);
  const capacidad_mesas = parseInt(document.getElementById('capacidad_mesas').value);

  if (!nombre_restaurante || !direccion || !num_mesas || !capacidad_mesas) {
    showMsg('err', 'Completa todos los campos obligatorios');
    return;
  }

  const aperturas = document.querySelectorAll('.horario-apertura');
  const horarios = Array.from(aperturas).map(el => ({
    dia: el.dataset.dia,
    apertura: el.value,
    cierre: document.querySelector(`.horario-cierre[data-dia="${el.dataset.dia}"]`).value
  })).filter(h => h.apertura && h.cierre);

  try {
    const r = await fetch(API + '/solicitudes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({ nombre_restaurante, telefono, direccion, descripcion, num_mesas, capacidad_mesas, horarios })
    });
    const d = await r.json();
    if (r.ok) {
      showMsg('ok', 'Solicitud enviada correctamente. Espera la aprobación.');
      setTimeout(() => window.location.href = '/restaurantes-page', 2000);
    } else {
      showMsg('err', d.detail || 'Error al enviar solicitud');
    }
  } catch {
    showMsg('err', 'No se pudo conectar al servidor');
  }
}

renderHorarios();
