const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://restaurante-reservas-g9hl.onrender.com';

let filtroActual = 'pendiente';

const rol = localStorage.getItem('rv_rol');
if (rol === 'admin') document.getElementById('nav-mi-restaurante').style.display = '';

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

function filtrar(estado) {
  filtroActual = estado;
  cargarSolicitudes();
}

function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

async function cargarSolicitudes() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = '/'; return; }

  try {
    let url = API + '/solicitudes';
    if (filtroActual) url += '?estado=' + filtroActual;

    const r = await fetch(url, {
      headers: { 'Authorization': 'Bearer ' + token }
    });

    if (r.status === 403) {
      window.location.href = '/restaurantes-page';
      return;
    }

    const data = await r.json();
    const lista = document.getElementById('lista');

    if (!data.length) {
      lista.innerHTML = '<div class="empty"><h3>Sin solicitudes</h3><p>No hay solicitudes en este estado.</p></div>';
      return;
    }

    function renderHorarios(horarios) {
      if (!horarios || !horarios.length) return '';
      return horarios.map(h =>
        `${h.dia}: ${h.apertura.slice(0,5)} - ${h.cierre.slice(0,5)}`
      ).join('<br/>');
    }

    lista.innerHTML = data.map((s, i) => `
      <div class="reserva-card" style="animation-delay:${i * 0.07}s; flex-direction:column; align-items:stretch;">
        <div class="reserva-info">
          <h3>🍽️ ${s.nombre_restaurante}</h3>
          <div class="meta">
            <strong>Solicitante:</strong> ${s.nombre_usuario} (${s.correo_usuario})<br/>
            📍 ${s.direccion}<br/>
            📞 ${s.telefono || 'N/A'}<br/>
            ${s.descripcion ? '📝 ' + s.descripcion + '<br/>' : ''}
            🪑 ${s.num_mesas} mesas · ${s.capacidad_mesas} personas c/u<br/>
            ${s.horarios && s.horarios.length ? '🕐 ' + renderHorarios(s.horarios) + '<br/>' : ''}
            📅 ${formatFecha(s.fecha_solicitud)}
          </div>
        </div>
        <span class="badge ${s.estado}" style="align-self:flex-start;margin-top:.5rem;">${s.estado}</span>
        ${s.estado === 'pendiente' ? `
          <div style="display:flex;gap:.5rem;margin-top:.75rem;">
            <button class="btn" style="background:linear-gradient(135deg,#4ade80,#22c55e);margin:0;flex:1;" onclick="aprobar(${s.id})">✅ Aprobar</button>
            <button class="btn" style="background:linear-gradient(135deg,#f87171,#ef4444);margin:0;flex:1;" onclick="rechazar(${s.id})">❌ Rechazar</button>
          </div>
        ` : ''}
      </div>
    `).join('');
  } catch {
    document.getElementById('lista').innerHTML = '<div class="empty"><p>Error al cargar solicitudes.</p></div>';
  }
}

async function aprobar(id) {
  const token = localStorage.getItem('rv_token');
  if (!confirm('¿Seguro que quieres aprobar esta solicitud?')) return;
  try {
    const r = await fetch(API + '/solicitudes/' + id + '/aprobar', {
      method: 'PUT',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const d = await r.json();
    if (r.ok) {
      showToast('ok', '✅ Solicitud aprobada');
      cargarSolicitudes();
    } else {
      showToast('err', d.detail || 'Error al aprobar');
    }
  } catch { showToast('err', 'No se pudo conectar al servidor'); }
}

async function rechazar(id) {
  const token = localStorage.getItem('rv_token');
  if (!confirm('¿Seguro que quieres rechazar esta solicitud?')) return;
  try {
    const r = await fetch(API + '/solicitudes/' + id + '/rechazar', {
      method: 'PUT',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const d = await r.json();
    if (r.ok) {
      showToast('ok', '✅ Solicitud rechazada');
      cargarSolicitudes();
    } else {
      showToast('err', d.detail || 'Error al rechazar');
    }
  } catch { showToast('err', 'No se pudo conectar al servidor'); }
}

cargarSolicitudes();
