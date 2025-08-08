from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .logger import setup_logger

app = FastAPI()
logger = setup_logger()


@app.get("/ping")
async def ping():
    logger.info("Received ping.")
    return {"message": "pong"}


@app.get("/data")
async def get_data():
    logger.info("Serving sample data")
    return {"data": "Sample payload for stress testing"}


@app.post("/submit")
async def submit_data(request: Request):
    payload = await request.json()
    logger.info(f"Data received: {payload}")
    return JSONResponse(
        status_code=201, content={"message": "Data received", "data": payload}
    )
