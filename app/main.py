from fastapi import FastAPI





#Creat Fastapi application
app = FastAPI()



@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint, return basic infomation for the API
    """
    return{
        "message": "Backend for users management with PostgreSQL",
        "version": "aqui va la version",
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