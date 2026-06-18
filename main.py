from fastapi import FastAPI
from loguru import logger

from app.api.routers.query_router import query_router

app = FastAPI()
app.include_router(query_router)
