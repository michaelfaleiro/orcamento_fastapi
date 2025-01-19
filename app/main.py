from tempfile import template
from fastapi import FastAPI
from app.routes.route_front import router as front_router
from app.config import database_url
from app.routes.route_api import router as api_router

app = FastAPI()



app.include_router(front_router)
app.include_router(api_router, prefix="/api")




