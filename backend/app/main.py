# app/main.py

from fastapi import FastAPI, HTTPException
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

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.9.0"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "GIRAFFE API",
        "version": "0.9.0",
        "status": "running",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }

# Include routers
app.include_router(user.router, prefix="/api/v1", tags=["User"])
app.include_router(data.router, prefix="/api/v1", tags=["Data"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(platforms.router, prefix="/api/v1", tags=["Platforms"])

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "path": request.url.path
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return {
        "error": str(exc),
        "status_code": 500,
        "path": request.url.path
    }