import logging

from motor.motor_asyncio import AsyncIOMotorClient

from . import config


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def connect_to_mongo() -> None:
    logging.info("Connecting to database...")
    db.client = AsyncIOMotorClient(
        config.DB_CONNECTION_URL,
        maxPoolSize=config.DB_MAX_CONNECTIONS_COUNT,
        minPoolSize=config.DB_MIN_CONNECTIONS_COUNT,
    )
    logging.info("Database connected!")


async def close_mongo_connection() -> None:
    logging.info("Closing database connection...")
    db.client.close()
    logging.info("Database closed!")