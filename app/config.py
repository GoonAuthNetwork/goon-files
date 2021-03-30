import os

from dotenv import load_dotenv

DEVELOPMENT = os.environ.get("development", "False") == "True"

# Only load .env on development
# Production should handle this via docker-compose, etc
if DEVELOPMENT:
    load_dotenv()

# Database settings
DB_MIN_CONNECTIONS_COUNT = int(os.environ.get("DB_MIN_CONNECTIONS_COUNT", "10"))
DB_MAX_CONNECTIONS_COUNT = int(os.environ.get("DB_MAX_CONNECTIONS_COUNT", "10"))

DB_CONNECTION_URL = os.environ.get("DB_CONNECTION_URL")

if DB_CONNECTION_URL is None:
    DB_MONGO_HOST = os.environ.get("DB_MONGO_HOST", "127.0.0.1")
    DB_MONGO_PORT = int(os.environ.get("DB_MONGO_PORT", "27017"))
    DB_MONGO_USER = os.environ.get("DB_MONGO_USER", "root")
    DB_MONGO_PASS = os.environ.get("DB_MONGO_PASS", "password")
    DB_MONGO_DB_NAME = os.environ.get("DB_MONGO_DB_NAME", "goon-files")

    DB_CONNECTION_URL = (
        f"mongodb://{DB_MONGO_USER}:{DB_MONGO_PASS}@"
        + f"{DB_MONGO_HOST}:{DB_MONGO_PORT}/{DB_MONGO_DB_NAME}"
    )
