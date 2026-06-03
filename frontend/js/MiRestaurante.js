const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://restaurante-reservas-g9hl.onrender.com';

const DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];

let restauranteActual = null;

const rol = localStorage.getItem('rv_rol');
if (rol !== 'admin') window.location.href = '/restaurantes-page';
if (rol === 'superadmin') document.getElementById('nav-solicitudes').style.display = '';

function logout() {
  localStorage.removeItem('rv_token');
  localStorage.removeItem('rv_rol');
  window.location.href = '/';
}

function showToast(type, text) {
  const t = document.getElementById('toast');
  t.className = 'toast ' + type;
  t.textContent = text;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 3000);
}

function showMsg(id, type, text) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = 'msg ' + type;
  el.textContent = text;
}

function getQueryParam(name) {
  const p = new URLSearchParams(window.location.search);
  return p.get(name);
}

async function iniciar() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = '/'; return; }

  const idParam = getQueryParam('id');
  if (idParam) {
    restauranteActual = parseInt(idParam);
    cargarDetalle(restauranteActual);
    return;
  }

  try {
    const r = await fetch(API + '/admin/mis-restaurantes', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const data = await r.json();

    if (data.length === 1) {
      restauranteActual = data[0].id;
      cargarDetalle(restauranteActual);
    } else {
      mostrarSelector(data);
    }
  } catch {
    document.getElementById('rest-header').innerHTML = '<p>Error al cargar restaurantes</p>';
  }
}

function mostrarSelector(restaurantes) {
  document.getElementById('selector').style.display = 'block';
  document.getElementById('gestion').style.display = 'none';
  const container = document.getElementById('selector-lista');

  container.innerHTML = restaurantes.map((r, i) => `
    <div class="rest-card" style="animation-delay:${i * 0.07}s; cursor:pointer" onclick="seleccionarRestaurante(${r.id})">
      <div class="card-icon">🍽️</div>
      <h3>${r.nombre}</h3>
      <p>${r.descripcion || ''}</p>
      <div class="meta">
        📍 ${r.direccion}<br/>
        📞 ${r.telefono || 'N/A'}
      </div>
      <button class="btn-reservar" style="margin-top:.75rem">Gestionar</button>
    </div>
  `).join('');
}

function seleccionarRestaurante(id) {
  window.location.href = '/mi-restaurante-page?id=' + id;
}

function cargarDetalle(id) {
  restauranteActual = id;
  document.getElementById('selector').style.display = 'none';
  document.getElementById('gestion').style.display = 'block';

  const token = localStorage.getItem('rv_token');

  fetch(API + '/admin/mi-restaurante/' + id, {
    headers: { 'Authorization': 'Bearer ' + token }
  })
    .then(r => r.json())
    .then(data => {
      document.getElementById('rest-nombre').value = data.nombre || '';
      document.getElementById('rest-direccion').value = data.direccion || '';
      document.getElementById('rest-telefono').value = data.telefono || '';
      document.getElementById('rest-descripcion').value = data.descripcion || '';

      renderHorarios(data.horarios || []);
      renderMesas(data.mesas || []);
      cargarReservas();
    })
    .catch(() => showMsg('msg-rest', 'err', 'Error al cargar datos del restaurante'));
}

function renderHorarios(horarios) {
  const container = document.getElementById('horarios-container');
  const map = {};
  horarios.forEach(h => { map[h.dia] = h; });

  container.innerHTML = DIAS.map(d => {
    const h = map[d] || { apertura: '', cierre: '' };
    return `
      <div class="row" style="margin-bottom:.5rem;align-items:center">
        <span style="flex:0 0 90px;text-transform:capitalize">${d}</span>
        <input type="time" class="horario-apertura" data-dia="${d}" value="${h.apertura}" style="flex:1"/>
        <span style="margin:0 .5rem">a</span>
        <input type="time" class="horario-cierre" data-dia="${d}" value="${h.cierre}" style="flex:1"/>
      </div>
    `;
  }).join('');
}

function guardarHorarios() {
  const aperturas = document.querySelectorAll('.horario-apertura');
  const horarios = Array.from(aperturas).map(el => ({
    dia: el.dataset.dia,
    apertura: el.value,
    cierre: document.querySelector(`.horario-cierre[data-dia="${el.dataset.dia}"]`).value
  })).filter(h => h.apertura && h.cierre);

  const token = localStorage.getItem('rv_token');
  fetch(API + '/admin/mi-restaurante/horarios?restaurante_id=' + restauranteActual, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify(horarios)
  })
    .then(r => r.json())
    .then(d => {
      if (d.mensaje) showToast('ok', d.mensaje);
      else showMsg('msg-horarios', 'err', d.detail || 'Error');
    })
    .catch(() => showMsg('msg-horarios', 'err', 'Error de conexión'));
}

function renderMesas(mesas) {
  const container = document.getElementById('mesas-container');
  if (!mesas.length) {
    container.innerHTML = '<p style="opacity:.6">No hay mesas registradas</p>';
    return;
  }
  container.innerHTML = mesas.map(m => `
    <div class="reserva-card" style="flex-direction:row;align-items:center;justify-content:space-between;padding:.75rem 1rem" id="mesa-${m.id}">
      <div>
        <strong>Mesa ${m.numero}</strong> — Capacidad: ${m.capacidad} personas
        ${!m.disponible ? ' <span style="color:#f87171">(no disponible)</span>' : ''}
      </div>
      <div style="display:flex;gap:.5rem">
        <button class="btn" style="margin:0;padding:.35rem .75rem;font-size:.85rem" onclick="editarMesa(${m.id})">Editar</button>
        <button class="btn" style="margin:0;padding:.35rem .75rem;font-size:.85rem;background:linear-gradient(135deg,#f87171,#ef4444)" onclick="eliminarMesa(${m.id})">Eliminar</button>
      </div>
    </div>
  `).join('');
}

function agregarMesa() {
  const numero = parseInt(document.getElementById('nueva-mesa-numero').value);
  const capacidad = parseInt(document.getElementById('nueva-mesa-capacidad').value);
  if (!numero || !capacidad) { showMsg('msg-mesas', 'err', 'Completa número y capacidad'); return; }

  const token = localStorage.getItem('rv_token');
  fetch(API + '/admin/mi-restaurante/mesas?restaurante_id=' + restauranteActual, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify({ numero_mesa: numero, capacidad })
  })
    .then(r => r.json())
    .then(d => {
      if (d.mensaje) {
        showToast('ok', d.mensaje);
        document.getElementById('nueva-mesa-numero').value = '';
        document.getElementById('nueva-mesa-capacidad').value = '';
        cargarDetalle(restauranteActual);
      } else {
        showMsg('msg-mesas', 'err', d.detail || 'Error');
      }
    })
    .catch(() => showMsg('msg-mesas', 'err', 'Error de conexión'));
}

function editarMesa(id) {
  const nuevaCap = prompt('Nueva capacidad:');
  if (!nuevaCap || isNaN(nuevaCap)) return;
  const token = localStorage.getItem('rv_token');
  fetch(API + '/admin/mi-restaurante/mesas/' + id + '?restaurante_id=' + restauranteActual, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify({ capacidad: parseInt(nuevaCap) })
  })
    .then(r => r.json())
    .then(d => {
      if (d.mensaje) { showToast('ok', d.mensaje); cargarDetalle(restauranteActual); }
      else showToast('err', d.detail || 'Error');
    })
    .catch(() => showToast('err', 'Error de conexión'));
}

function eliminarMesa(id) {
  if (!confirm('¿Seguro que quieres eliminar esta mesa?')) return;
  const token = localStorage.getItem('rv_token');
  fetch(API + '/admin/mi-restaurante/mesas/' + id + '?restaurante_id=' + restauranteActual, {
    method: 'DELETE',
    headers: { 'Authorization': 'Bearer ' + token }
  })
    .then(r => r.json())
    .then(d => {
      if (d.mensaje) { showToast('ok', d.mensaje); cargarDetalle(restauranteActual); }
      else showToast('err', d.detail || 'Error');
    })
    .catch(() => showToast('err', 'Error de conexión'));
}

function guardarRestaurante() {
  const data = {
    nombre: document.getElementById('rest-nombre').value.trim(),
    direccion: document.getElementById('rest-direccion').value.trim(),
    telefono: document.getElementById('rest-telefono').value.trim(),
    descripcion: document.getElementById('rest-descripcion').value.trim()
  };

  if (!data.nombre || !data.direccion) {
    showMsg('msg-rest', 'err', 'Nombre y dirección son obligatorios');
    return;
  }

  const token = localStorage.getItem('rv_token');
  fetch(API + '/admin/mi-restaurante?restaurante_id=' + restauranteActual, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify(data)
  })
    .then(r => r.json())
    .then(d => {
      if (d.mensaje) showToast('ok', d.mensaje);
      else showMsg('msg-rest', 'err', d.detail || 'Error');
    })
    .catch(() => showMsg('msg-rest', 'err', 'Error de conexión'));
}

let tabActual = 'pendiente';

function switchTab(tab) {
  tabActual = tab;
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tab);
  });
  renderReservas();
}

function renderReservas() {
  const container = document.getElementById('reservas-container');
  const reservas = window._reservasPorEstado?.[tabActual];
  if (!reservas || !reservas.length) {
    container.innerHTML = '<p style="opacity:.6">No hay reservas ' + (tabActual === 'pendiente' ? 'pendientes' : tabActual + 's') + '</p>';
    return;
  }
  container.innerHTML = reservas.map(r => `
    <div class="reserva-card" style="flex-direction:column;align-items:stretch;padding:.75rem 1rem">
      <div class="reserva-info">
        <strong>Mesa ${r.mesa}</strong> · ${r.personas} personas
        <div class="meta">
          📅 ${r.fecha} 🕐 ${r.hora.slice(0,5)}<br/>
          👤 ${r.cliente} (${r.correo_cliente})
        </div>
      </div>
      <div style="display:flex;gap:.5rem;align-items:center;margin-top:.5rem">
        <span class="badge ${r.estado}">${r.estado}</span>
        ${r.estado === 'pendiente' ? `<button class="btn" style="margin:0;padding:.35rem .75rem;font-size:.85rem;background:linear-gradient(135deg,#4ade80,#22c55e)" onclick="confirmarReserva(${r.id})">✅ Confirmar</button>` : ''}
      </div>
    </div>
  `).join('');
}

function cargarReservas() {
  const token = localStorage.getItem('rv_token');
  if (!token) return;

  const fecha = document.getElementById('filtro-fecha').value;

  Promise.all(
    ['pendiente', 'confirmada', 'cancelada'].map(estado => {
      let url = API + '/admin/mi-restaurante/reservas?restaurante_id=' + restauranteActual + '&estado=' + estado;
      if (fecha) url += '&fecha=' + fecha;
      return fetch(url, { headers: { 'Authorization': 'Bearer ' + token } }).then(r => {
        if (!r.ok) throw new Error(estado + ' returned ' + r.status);
        return r.json();
      });
    })
  ).then(([pendientes, confirmadas, canceladas]) => {
    window._reservasPorEstado = {
      pendiente: pendientes,
      confirmada: confirmadas,
      cancelada: canceladas
    };
    document.getElementById('count-pendiente').textContent = pendientes.length;
    document.getElementById('count-confirmada').textContent = confirmadas.length;
    document.getElementById('count-cancelada').textContent = canceladas.length;
    renderReservas();
  }).catch(err => {
    document.getElementById('reservas-container').innerHTML =
      '<p style="color:var(--err)">Error: ' + err.message + '</p>';
  });
}

function confirmarReserva(id) {
  if (!confirm('¿Confirmar esta reserva?')) return;
  const token = localStorage.getItem('rv_token');
  fetch(API + '/admin/mi-restaurante/reservas/' + id + '/confirmar?restaurante_id=' + restauranteActual, {
    method: 'PUT',
    headers: { 'Authorization': 'Bearer ' + token }
  })
    .then(r => r.json())
    .then(d => {
      if (d.mensaje) { showToast('ok', d.mensaje); cargarReservas(); }
      else showToast('err', d.detail || 'Error');
    })
    .catch(() => showToast('err', 'Error de conexión'));
}

iniciar();
