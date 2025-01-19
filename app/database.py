from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient('mongodb+srv://mongodb:mongodb@cluster.7rwcs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster')
db = client['orcamentos']


