# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, data, analysis, platforms
from app.database.config import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GIRAFFE API",
    description="API for GIRAFFE - Data Analysis and Visualization Platform",
    version="0.9.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router, prefix="/api/v1", tags=["User"])
app.include_router(data.router, prefix="/api/v1", tags=["Data"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(platforms.router, prefix="/api/v1", tags=["Platforms"])

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "GIRAFFE API is running",
        "version": "0.9.0"
    }