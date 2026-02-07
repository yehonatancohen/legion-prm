from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import redirect
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS Fix
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # Not allowed with credentials
    allow_origin_regex=".*",  # Allow ALL origins via regex to support credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Starting up with CORS policy: allow_origin_regex='.*' (ALL ORIGINS ALLOWED)")

# Include the Redirect Router (root level for short links)
app.include_router(redirect.router, tags=["redirect"])

from app.api.endpoints import auth, admin, agent
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])
from app.api.endpoints import whatsapp
app.include_router(whatsapp.router, prefix="/api/v1/whatsapp", tags=["whatsapp"])

# Contact Pool and VCF Management
from app.api.endpoints import contacts
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])

# Campaigns Management
from app.api.endpoints import campaigns
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])

# Placeholder for API V1
# app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Distributed Agent Platform API", "status": "running"}
