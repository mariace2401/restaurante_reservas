from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.routes import auth, reservas, restaurantes

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="frontend"), name="static")


app.include_router(auth.router)
app.include_router(reservas.router)
app.include_router(restaurantes.router)


@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/index.html") as f:
        return f.read()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/restaurantes-page", response_class=HTMLResponse)
def restaurantes_page():
    with open("frontend/Restaurantes.html") as f:
        return f.read()

@app.get("/reservar-page", response_class=HTMLResponse)
def reservar_page():
    with open("frontend/Reservar.html") as f:
        return f.read()

@app.get("/mis-reservas-page", response_class=HTMLResponse)
def mis_reservas_page():
    with open("frontend/Misreservas.html") as f:
        return f.read()