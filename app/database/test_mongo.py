import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongo():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    try:
        info = await client.server_info()
        print("✅ Conexión a MongoDB exitosa:", info)
    except Exception as e:
        print("❌ Error de conexión a MongoDB:", e)

if __name__ == "__main__":
    asyncio.run(test_mongo())