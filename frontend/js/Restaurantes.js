const API = "http://127.0.0.1:8000";
const ICONOS = ['🍽️','🍜','🥞','🍗','🥩','🍱'];

function logout() {
  localStorage.removeItem('rv_token');
  localStorage.removeItem('rv_rol');
  window.location.href = '/';
}

async function cargarRestaurantes() {
  const token = localStorage.getItem('rv_token');
  if (!token) { window.location.href = '/'; return; }

  try {
    const r = await fetch(API + '/restaurantes');
    const data = await r.json();
    const grid = document.getElementById('grid');

    if (!data.length) {
      grid.innerHTML = '<div class="empty">No hay restaurantes disponibles.</div>';
      return;
    }

    grid.innerHTML = data.map((rest, i) => `
      <div class="rest-card" style="animation-delay:${i * 0.07}s">
        <div class="card-icon">${ICONOS[i % ICONOS.length]}</div>
        <h3>${rest.nombre}</h3>
        <p>${rest.descripcion || 'Restaurante en Pereira'}</p>
        <div class="meta">
          📍 <span>${rest.direccion}</span><br/>
          📞 <span>${rest.telefono || 'N/A'}</span>
        </div>
        <button class="btn-reservar" onclick="window.location.href='/reservar-page?id=${rest.id}&nombre=${encodeURIComponent(rest.nombre)}'">
          Reservar mesa
        </button>
      </div>
    `).join('');
  } catch {
    document.getElementById('grid').innerHTML = '<div class="empty">Error al cargar restaurantes.</div>';
  }
}

cargarRestaurantes();