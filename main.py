from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Item Catalog API",
    description="A stateless API returning a list of items",
    version="1.0.0",
)


class Item(BaseModel):
    id: int
    name: str
    category: str
    price: float
    in_stock: bool


# Sample in-memory catalog
ITEMS: List[Item] = [
    Item(id=1, name="Mechanical Keyboard", category="Electronics", price=89.99, in_stock=True),
    Item(id=2, name="Wireless Mouse", category="Electronics", price=49.99, in_stock=True),
    Item(id=3, name="Coffee Mug", category="Lifestyle", price=14.50, in_stock=True),
    Item(id=4, name="Notebook", category="Stationery", price=7.00, in_stock=False),
]


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "FastAPI service is running"}


@app.get("/items", response_model=List[Item], tags=["Items"])
def get_items():
    """Retrieve the full list of items."""
    return ITEMS


@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
def get_item_by_id(item_id: int):
    """Retrieve a single item by its ID."""
    for item in ITEMS:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")