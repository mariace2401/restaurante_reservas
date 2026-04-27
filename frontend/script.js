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

        // 🔥 ocultar login y mostrar reservas
        document.getElementById("loginBox").style.display = "none";
        document.getElementById("registroBox").style.display = "none";
        document.getElementById("reservaBox").style.display = "block";
    })
    .catch(() => {
        document.getElementById("mensaje").innerText = "❌ Error en login";
    });
}


function registrar() {
    const usuario = document.getElementById("nuevo_usuario").value;
    const password = document.getElementById("nuevo_password").value;

    fetch("http://127.0.0.1:8000/auth/register", {
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
        document.getElementById("mensaje").innerText =
            "✅ Usuario registrado";

        // volver al login
        mostrarLogin();
    })
    .catch(() => {
        document.getElementById("mensaje").innerText =
            "❌ Error al registrar";
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


// 🔹 CAMBIOS DE VISTA
function mostrarRegistro() {
    document.getElementById("loginBox").style.display = "none";
    document.getElementById("registroBox").style.display = "block";
}

function mostrarLogin() {
    document.getElementById("registroBox").style.display = "none";
    document.getElementById("loginBox").style.display = "block";
}