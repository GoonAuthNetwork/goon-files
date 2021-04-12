from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from app import config


class Database:
    client: AsyncIOMotorClient = None
    engine: AIOEngine = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def get_engine() -> AIOEngine:
    return db.engine


async def connect_to_mongo() -> None:
    logger.info("Connecting to database...")

    db.client = AsyncIOMotorClient(
        config.DB_CONNECTION_URL,
        maxPoolSize=config.DB_MAX_CONNECTIONS_COUNT,
        minPoolSize=config.DB_MIN_CONNECTIONS_COUNT,
    )
    db.engine = AIOEngine(db.client, config.DB_MONGO_DB_NAME)

    logger.info("Database connected!")


async def close_mongo_connection() -> None:
    logger.info("Closing database connection...")

    db.engine = None
    db.client.close()

    logger.info("Database closed!")
