from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="Minha API FastAPI"
)

app.include_router(users.router)


@app.get("/")
def home():
    return {
        "message": "API funcionando."
    }