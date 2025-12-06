from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, database
from .routers import market, portfolio, auth, alerts
from fastapi.middleware.cors import CORSMiddleware

# Create all database tables defined in models.py
# This is a simple way to initialize the DB. In production, use Alembic migrations.
models.Base.metadata.create_all(bind=database.engine)

# Initialize the FastAPI application
app = FastAPI(title="Stock Manager")

# Configure CORS (Cross-Origin Resource Sharing).
# This allows our React frontend (running on a different port) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],
)

# Include routers. This keeps the code organized by feature.
app.include_router(auth.router)
app.include_router(market.router)
app.include_router(portfolio.router)
app.include_router(alerts.router)

@app.get("/")
def read_root():
    return {"message": "Stock Manager API is running"}
