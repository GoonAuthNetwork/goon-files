import os

from dotenv import load_dotenv

DEVELOPMENT = os.environ.get("development", "False") == "True"

# Only load .env on development
# Production should handle this via docker-compose, etc
if DEVELOPMENT:
    load_dotenv()

# Database settings
DB_MIN_CONNECTIONS_COUNT = int(os.getenv("DB_MIN_CONNECTIONS_COUNT", 10))
DB_MAX_CONNECTIONS_COUNT = int(os.getenv("DB_MAX_CONNECTIONS_COUNT", 10))

DB_CONNECTION_URL = os.getenv("DB_CONNECTION_URL")

if DB_CONNECTION_URL is None:
    DB_MONGO_HOST = os.getenv("DB_MONGO_HOST", "127.0.0.1")
    DB_MONGO_PORT = int(os.getenv("DB_MONGO_PORT", 27017))
    DB_MONGO_USER = os.getenv("DB_MONGO_USER", "root")
    DB_MONGO_PASS = os.getenv("DB_MONGO_PASS", "password")
    DB_MONGO_DB_NAME = os.getenv("DB_MONGO_DB_NAME", "goon-files")

    DB_CONNECTION_URL = (
        f"mongodb://{DB_MONGO_USER}:{DB_MONGO_PASS}@"
        + f"{DB_MONGO_HOST}:{DB_MONGO_PORT}/"
    )

# Logger settings
LOGGING_CONFIG = {
    "file": {
        "path": os.getenv("LOGGING_FILE_PATH", "/var/logs"),
        "name": os.getenv("LOGGING_FILE_NAME", "/access.log"),
        "rotation": os.getenv("LOGGING_FILE_ROTATION", "20 days"),
        "retention": os.getenv("LOGGING_FILE_PETENTION", "1 months"),
    },
    "level": os.getenv("LOGGING_LEVEL", "info"),
    "format": os.getenv(
        "LOGGING_FORMAT",
        "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        + "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    ),
}
