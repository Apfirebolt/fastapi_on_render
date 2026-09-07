import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "express-recipe")

mongodb_client: Optional[AsyncIOMotorClient] = None
db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongodb_client, db
    mongodb_client = AsyncIOMotorClient(MONGO_URI)
    db = mongodb_client[DATABASE_NAME]
    try:
        await mongodb_client.admin.command("ping")
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
    yield
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed.")


app = FastAPI(
    title="Item & User Catalog API",
    description="FastAPI service connected to MongoDB",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --------------------------------------------------
# Schemas
# --------------------------------------------------

class ItemBase(BaseModel):
    name: str
    category: str
    price: float
    in_stock: bool = True
    image_url: str = ""


class ItemResponse(ItemBase):
    id: str = Field(alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


# User Response Schema (Excludes password field for security)
class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: EmailStr
    is_admin: bool = Field(alias="isAdmin")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


# --------------------------------------------------
# Web UI Routes
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
async def home(request: Request):
    items_cursor = db["items"].find()
    raw_items = await items_cursor.to_list(length=100)
    items = [{**item, "id": str(item["_id"])} for item in raw_items]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Modern Catalog", "items": items},
    )


# --------------------------------------------------
# User Endpoints
# --------------------------------------------------

@app.get(
    "/users",
    response_model=List[UserResponse],
    tags=["Users"],
    summary="Get all users",
)
async def get_users(limit: int = 50, skip: int = 0):
    """
    Fetch a paginated list of users.
    Excludes the hashed password and __v fields from the database query.
    """
    # Projection: 0 excludes the field
    users_cursor = (
        db["users"]
        .find({}, {"password": 0, "__v": 0})
        .skip(skip)
        .limit(limit)
    )
    raw_users = await users_cursor.to_list(length=limit)

    return [{**user, "_id": str(user["_id"])} for user in raw_users]


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get user by ID",
)
async def get_user_by_id(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    user = await db["users"].find_one(
        {"_id": ObjectId(user_id)},
        {"password": 0, "__v": 0},
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {**user, "_id": str(user["_id"])}


# --------------------------------------------------
# Item Endpoints
# --------------------------------------------------

@app.get("/items", response_model=List[ItemResponse], tags=["Items"])
async def get_items():
    cursor = db["items"].find()
    raw_items = await cursor.to_list(length=100)
    return [{**item, "_id": str(item["_id"])} for item in raw_items]