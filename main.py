from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, seed_data
from app.routers import chat, appointments, services

# Create all DB tables
Base.metadata.create_all(bind=engine)
# Seed with demo data
seed_data()

app = FastAPI(title="Bright Smile Dental Clinic - AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(services.router, prefix="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Dental Assistant API is running"}