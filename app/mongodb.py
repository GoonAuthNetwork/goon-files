from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from . import config


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def connect_to_mongo() -> None:
    logger.info("Connecting to database...")
    db.client = AsyncIOMotorClient(
        config.DB_CONNECTION_URL,
        maxPoolSize=config.DB_MAX_CONNECTIONS_COUNT,
        minPoolSize=config.DB_MIN_CONNECTIONS_COUNT,
    )
    logger.info("Database connected!")


async def close_mongo_connection() -> None:
    logger.info("Closing database connection...")
    db.client.close()
    logger.info("Database closed!")
