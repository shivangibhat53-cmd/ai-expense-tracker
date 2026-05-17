from fastapi import FastAPI
from app.db.base import Base
from app.core.logging import logger
from app.api.v1.router import api_router
from app.models import user  #important to register model
from fastapi.responses import JSONResponse


app = FastAPI(
    title = "API Finance Platform",
    version = "1.0.0"
)
logger.info("🚀 FastAPI application starting up...")
logger.info("Attaching api/v1/router to the app")
app.include_router(api_router, prefix="/api/v1")
@app.exception_handler(Exception)
async def global_exception_handler(request,exc):
    logger.exception(f"Unhandler exception: {str(exc)}")

    return JSONResponse(
        status_code = 500,
        content ={"detail" : "Internal Server Error"}
    )
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message":"Backend is running"}