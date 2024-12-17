# app/main.py

from fastapi import FastAPI
from app.routes import user, data, analysis

app = FastAPI()

# Include routes
app.include_router(user.router)
app.include_router(data.router)
app.include_router(analysis.router)

@app.get("/")
def root():
    return {"message": "API is running!"}