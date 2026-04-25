from fastapi import FastAPI
from backend.routes import auth, reservas, restaurantes


app = FastAPI()

app.include_router(auth.router)
app.include_router(reservas.router)
app.include_router(restaurantes.router)


@app.get("/")
def root():
    return {"mensaje": "API Restaurante Reservas"}


@app.get("/health")
def health():
    return {"status": "ok"}