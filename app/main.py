from fastapi import FastAPI
from .mongodb import connect_to_mongo, close_mongo_connection
from .fastapi_logging import CustomizeLogger

app = FastAPI(title="Goon Files")
app.logger = CustomizeLogger.make_logger()

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)


@app.get("/")
async def root():
    return {"message": "Hello world"}
