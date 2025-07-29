from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routes import auth_router, user_router
from app.config import settings


#Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#Creat Fastapi application
app = FastAPI(
    title = settings.APP_NAME,
    version = settings.APP_VERSION,
    description = "API for users management with PostgreSQL",
    debug = settings.DEBUG
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application stopped")

#CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], 
    allow_credentials = True,
    allow_methods ="*",
    allow_headers = ["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint, return basic infomation for the API
    """
    return{
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/docs",
    }

@app.get("/status", tags=["Health"])
async def health_check():
    """
    Endpoint for monitoring health check
    """
    return{"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
        )