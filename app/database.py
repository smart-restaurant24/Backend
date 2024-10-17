from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

client = AsyncIOMotorClient(config("MONGODB_URL"))
db = client.restaurant_app

async def init_db():
    # You can add initial setup here if needed
    pass

async def filter_menu(restaurant_id: str, preferences: dict):
    query = {"restaurantId": restaurant_id}

    if preferences["dietary"]:
        query["$and"] = [{f"dietaryFlags.is{pref}": True} for pref in preferences["dietary"]]

    if preferences["cuisine"]:
        query["cuisine"] = {"$in": preferences["cuisine"]}

    if preferences["price_range"]:
        if preferences["price_range"] == "low":
            query["price"] = {"$lte": 15}
        elif preferences["price_range"] == "medium":
            query["price"] = {"$gt": 15, "$lte": 30}
        elif preferences["price_range"] == "high":
            query["price"] = {"$gt": 30}

    if preferences["ingredients"]["exclude"]:
        query["ingredients"] = {"$nin": preferences["ingredients"]["exclude"]}

    if preferences["spiciness"]:
        query["spiciness"] = {"$lte": preferences["spiciness"]}

    menu_items = await db.dishes.find(query).sort("popularity", -1).limit(15).to_list(15)
    return menu_items