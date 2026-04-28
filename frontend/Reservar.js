const API = "http://127.0.0.1:8000";
let mesaSeleccionada = null;

function logout() {
  localStorage.removeItem('rv_token');
  localStorage.removeItem('rv_rol');
  window.location.href = 'index.html';
}

function getParams() {
  const p = new URLSearchParams(window.location.search);
  return { id: p.get('id'), nombre: p.get('nombre') };
}

function showMsg(type, text) {
  const el = document.getElementById('msg');
  el.className = 'msg ' + type;
  el.textContent = text;
}

function seleccionarMesa(id, numero, capacidad) {
  mesaSeleccionada = { id, capacidad };
  document.querySelectorAll('.mesa-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('mesa-' + id).classList.add('selected');
  document.getElementById('mesa-seleccionada').textContent =
    `Mesa ${numero} seleccionada — capacidad ${capacidad} personas`;
}

async function cargarDetalle() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = 'index.html'; return; }

  const { id, nombre } = getParams();
  document.getElementById('rest-nombre').textContent = decodeURIComponent(nombre || '');

  try {
    const r = await fetch(`${API}/restaurantes/${id}`);
    const d = await r.json();
    document.getElementById('rest-direccion').textContent = d.direccion;

    document.getElementById('horarios').innerHTML = d.horarios.map(h =>
      `<span class="horario-tag">${h.dia}: ${h.apertura.slice(0,5)}–${h.cierre.slice(0,5)}</span>`
    ).join('');

    if (!d.mesas_disponibles.length) {
      document.getElementById('mesas').innerHTML =
        '<p style="color:var(--muted);font-size:.85rem">No hay mesas disponibles.</p>';
    } else {
      document.getElementById('mesas').innerHTML = d.mesas_disponibles.map(m => `
        <div class="mesa-card" id="mesa-${m.id_mesa}" onclick="seleccionarMesa(${m.id_mesa}, ${m.numero}, ${m.capacidad})">
          <div class="num">Mesa ${m.numero}</div>
          <div class="cap">${m.capacidad} personas</div>
        </div>
      `).join('');
    }
  } catch {
    showMsg('err', 'Error al cargar el restaurante.');
  }
}

async function doReservar() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = 'index.html'; return; }
  if (!mesaSeleccionada) { showMsg('err', 'Selecciona una mesa primero'); return; }

  const fecha    = document.getElementById('fecha').value;
  const hora     = document.getElementById('hora').value;
  const personas = parseInt(document.getElementById('personas').value);

  if (!fecha || !hora || !personas) { showMsg('err', 'Completa todos los campos'); return; }
  if (personas > mesaSeleccionada.capacidad) {
    showMsg('err', `La mesa tiene capacidad para ${mesaSeleccionada.capacidad} personas`);
    return;
  }

  try {
    const r = await fetch(API + '/reservas', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({ id_mesa: mesaSeleccionada.id, fecha, hora, personas })
    });
    const d = await r.json();
    if (r.ok) {
      showMsg('ok', '¡Reserva creada! Redirigiendo...');
      setTimeout(() => window.location.href = 'mis-reservas.html', 1500);
    } else {
      showMsg('err', d.detail || 'Error al crear la reserva');
    }
  } catch { showMsg('err', 'No se pudo conectar al servidor'); }
}

document.getElementById('fecha').min = new Date().toISOString().split('T')[0];
cargarDetalle();