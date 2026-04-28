const API = "http://127.0.0.1:8000";

function logout() {
  localStorage.removeItem('rv_token');
  localStorage.removeItem('rv_rol');
  window.location.href = 'index.html';
}

function showToast(type, text) {
  const t = document.getElementById('toast');
  t.className = 'toast ' + type;
  t.textContent = text;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 3000);
}

function formatFecha(f) {
  const [y, m, d] = f.split('-');
  return `${d}/${m}/${y}`;
}

async function cargarReservas() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = 'index.html'; return; }

  try {
    const r = await fetch(API + '/reservas/mis-reservas', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const data = await r.json();
    const lista = document.getElementById('lista');

    if (!data.length) {
      lista.innerHTML = `
        <div class="empty">
          <h3>Sin reservas activas</h3>
          <p>¿Listo para tu próxima experiencia? <a href="restaurantes.html">Ver restaurantes</a></p>
        </div>`;
      return;
    }

    lista.innerHTML = data.map((res, i) => `
      <div class="reserva-card" style="animation-delay:${i * 0.07}s" id="card-${res.id}">
        <div class="reserva-info">
          <h3>🍽️ ${res.restaurante}</h3>
          <div class="meta">
            📅 <span>${formatFecha(res.fecha)}</span> &nbsp;·&nbsp;
            🕐 <span>${res.hora.slice(0,5)}</span> &nbsp;·&nbsp;
            👥 <span>${res.personas} personas</span> &nbsp;·&nbsp;
            Mesa <span>${res.mesa}</span>
          </div>
        </div>
        <span class="badge ${res.estado}">${res.estado}</span>
        <button class="btn-cancelar" onclick="cancelar(${res.id})">Cancelar</button>
      </div>
    `).join('');
  } catch {
    document.getElementById('lista').innerHTML = '<div class="empty"><p>Error al cargar reservas.</p></div>';
  }
}

async function cancelar(id) {
  const token = localStorage.getItem('rv_token');
  if (!confirm('¿Seguro que quieres cancelar esta reserva?')) return;
  try {
    const r = await fetch(`${API}/reservas/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const d = await r.json();
    if (r.ok) {
      showToast('ok', '✅ Reserva cancelada');
      document.getElementById('card-' + id)?.remove();
      if (!document.querySelector('.reserva-card')) {
        document.getElementById('lista').innerHTML = `
          <div class="empty">
            <h3>Sin reservas activas</h3>
            <p><a href="restaurantes.html">Ver restaurantes</a></p>
          </div>`;
      }
    } else {
      showToast('err', d.detail || 'Error al cancelar');
    }
  } catch { showToast('err', 'No se pudo conectar al servidor'); }
}

cargarReservas();