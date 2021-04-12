from fastapi import FastAPI
from app.logging_hook import customize_logging
from app.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import user

app = FastAPI(title="Goon Files")
app.logger = customize_logging()

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Hello root"}
