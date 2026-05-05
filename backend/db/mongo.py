from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client.ims
        
    async def close(self):
        if self.client:
            self.client.close()

mongo_client = MongoDBClient()
