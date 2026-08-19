from fastapi import FastAPI, Depends

from database.database import Base, engine
from database import models
from database.models import User

from api.auth import router as auth_router
from auth.dependencies import get_current_user


app = FastAPI()


# Create database tables
Base.metadata.create_all(bind=engine)


# Register authentication routes
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Personal Knowledge Base API is running!"
    }


@app.get("/me", response_model=dict)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email
    }