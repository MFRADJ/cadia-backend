# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.api.routes import auth, users
from app.api import deps
from app.core.config import settings
from app.db.session import engine, Base

# Création des tables avec un gestionnaire de contexte
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Création des tables au démarrage
    Base.metadata.create_all(bind=engine)
    print("🚀 Base de données initialisée!")
    yield
    # Nettoyage à l'arrêt (optionnel)
    print("🛑 Application arrêtée!")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API pour le système d'authentification CADIA",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,  # Utilisation du gestionnaire de contexte
)

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Point d'entrée API
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API CADIA"}

# Endpoint de vérification de l'état de santé
@app.get("/health")
async def health_check():
    return {"status": "ok", "api_version": "1.0.0"}

# Vérification de la connexion à la base de données
@app.get("/db-test")
async def test_db(db: Session = Depends(deps.get_db)):
    try:
        # Exécuter une requête simple pour tester la connexion
        db.execute("SELECT 1")
        return {"status": "Base de données connectée avec succès"}
    except Exception as e:
        return {"status": "Erreur de connexion à la base de données", "error": str(e)}

# Inclusion des routeurs
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentification"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["utilisateurs"]
)

# Point d'entrée pour exécuter l'application avec Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)