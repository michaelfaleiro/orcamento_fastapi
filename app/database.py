from motor.motor_asyncio import AsyncIOMotorClient
from app.config import database_url

client = AsyncIOMotorClient(database_url)
db = client['orcamentos']


