from fastapi import FastAPI
from loguru import logger

from app.api.routers.query_router import query_router
from app.api.routers.user_router import user_router

app = FastAPI()
app.include_router(query_router)
app.include_router(user_router)
