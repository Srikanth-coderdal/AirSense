import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import get_pool, close_pool, check_db_connection
from backend.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("AirSenseAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database connection pool is initialized
    try:
        get_pool()
        logger.info("Application startup: DB pool ready.")
    except Exception as e:
        logger.warning(f"Application startup: DB connection could not be established immediately: {e}")
    yield
    # Shutdown: clean up connection pool
    close_pool()
    logger.info("Application shutdown: DB pool closed.")


app = FastAPI(
    title="AirSense API",
    version="1.0.0",
    description="Backend API service for AirSense real-time air quality monitoring, forecasting, and compliance platform.",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint checking application and database connection status."""
    db_healthy = check_db_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "AirSense API",
        "database": "connected" if db_healthy else "disconnected",
    }
