from typing import List
from fastapi import APIRouter, HTTPException
from app.database import db
from app.models import Recommendation

router = APIRouter()


@router.get("/recommendation/{user_id}", response_model=List[Recommendation])
async def get_recommendation(user_id: str):
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recommended_dishes = await db.dishes.find({
        "cuisine": {"$in": user["preferences"]["favoriteCuisines"]},
        "price": {"$lte": user["preferences"]["maxPrice"]},
    }).sort("popularity", -1).limit(5).to_list(5)

    return [Recommendation(**dish, score=dish.get("popularity", 0)) for dish in recommended_dishes]