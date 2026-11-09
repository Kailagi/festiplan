from fastapi import FastAPI
from app.config import settings
from app.api import festivals,artists,stages,concerts,incidents
from app.bootstrap.database import initialize_database
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app=FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API de gestion d'un festival fictif",
    lifespan=lifespan,
)

for router in (festivals.router,artists.router,stages.router,concerts.router,incidents.router): app.include_router(router)

@app.get("/")
def health(): return {"message":"Bienvenue sur FestiPlan","status":"ok"}
