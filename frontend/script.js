let token = null;

function login() {
    const usuario = document.getElementById("usuario").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: usuario,
            password: password
        })
    })
    .then(res => res.json())
    .then(data => {
        token = data.access_token;
        document.getElementById("mensaje").innerText = "✅ Login exitoso";
    })
    .catch(() => {
        document.getElementById("mensaje").innerText = "❌ Error en login";
    });
}


function hacerReserva() {
    const fecha = document.getElementById("fecha").value;
    const personas = document.getElementById("personas").value;

    fetch("http://127.0.0.1:8000/reservas/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            id_mesa: 1,
            fecha: fecha,
            hora: "18:00",
            personas: parseInt(personas)
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("mensaje").innerText =
            "✅ Reserva creada";
    })
    .catch(() => {
        document.getElementById("mensaje").innerText =
            "❌ Error al reservar";
    });
}