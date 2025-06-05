from fastapi import FastAPI


from app.config import settings


#Creat Fastapi application
app = FastAPI(
    title = settings.APP_NAME,
    version = settings.APP_VERSION,
    description = "API for users management with PostgreSQL",
    debug = settings.DEBUG
)



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