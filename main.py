import traceback
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend.init_db import init_db
from backend.seed import seed_data


from backend.routes import auth, reservas, restaurantes

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_data()
    yield


app = FastAPI(lifespan=lifespan)

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

@app.get("/debug-db")
def debug_db():
    try:
        from backend.database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM restaurante")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {"db_url_set": bool(os.getenv("DATABASE_URL")), "restaurantes": count}
    except Exception as e:
        return {"db_url_set": bool(os.getenv("DATABASE_URL")), "error": str(e), "traceback": traceback.format_exc()}


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