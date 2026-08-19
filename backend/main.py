from fastapi import FastAPI

from database.database import Base, engine
from database import models

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Personal Knowledge Base API is running!"}