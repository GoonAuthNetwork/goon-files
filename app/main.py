from fastapi import FastAPI
from .mongodb import connect_to_mongo, close_mongo_connection
from .logging_hook import customize_logging

app = FastAPI(title="Goon Files")
app.logger = customize_logging()

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)


@app.get("/")
async def root():
    return {"message": "Hello world"}
