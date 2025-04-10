from fastapi import FastAPI
# Use relative import since database.py is in the same directory
from .database import connect_to_mongo, close_mongo_connection
# Import the new router
from .routers import word_pairs

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(word_pairs.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
