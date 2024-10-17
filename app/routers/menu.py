from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List
from app.models import MenuItem
from app.database import db

router = APIRouter()

@router.get("/api/cuisines/{restaurant_id}")
async def get_cuisines(restaurant_id: str):
    restaurant_id = ObjectId(restaurant_id)
    restaurant = await db.restaurants.find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant.get("cuisine", [])

@router.get("/api/menu/{restaurant_id}/{cuisine}", response_model=List[MenuItem])
async def get_menu(restaurant_id: str, cuisine: str):
    restaurant_id = ObjectId(restaurant_id)
    menu_items = await db.dishes.find({"restaurantId": restaurant_id, "cuisine": cuisine}).to_list(1000)
    if not menu_items:
        raise HTTPException(status_code=404, detail="Menu not found" + restaurant_id.__str__() +cuisine )
    return [MenuItem(**item) for item in menu_items]

@router.get("/api/restaurant/{restaurant_id}")
async def get_restaurant_info(restaurant_id: str):
    restaurant_id = ObjectId(restaurant_id)
    print("Restaurant:", restaurant_id)
    restaurant = await db.restaurants.find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found" + restaurant_id.__str__())
    return {
        "name": restaurant["name"],
        "logo": restaurant.get("logo", "🍽️")  # Default to a plate emoji if no logo
    }