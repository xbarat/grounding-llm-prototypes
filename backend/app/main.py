# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, data, analysis
from app.database.config import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TypeRacer Analytics API",
    description="API for analyzing TypeRacer performance data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(user.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "TypeRacer Analytics API is running!",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }