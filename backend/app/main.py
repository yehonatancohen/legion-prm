from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import redirect
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS Fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Redirect Router (root level for short links)
app.include_router(redirect.router, tags=["redirect"])

from app.api.endpoints import auth, admin, agent
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])
from app.api.endpoints import whatsapp
app.include_router(whatsapp.router, prefix="/api/v1/whatsapp", tags=["whatsapp"])

# Placeholder for API V1
# app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Distributed Agent Platform API", "status": "running"}
