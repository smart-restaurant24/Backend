from bson import ObjectId
from fastapi import APIRouter, HTTPException
from ..models import ChatMessage
from ..services.ollama_service import get_ollama_response
from ..database import db, filter_menu
from ..utils.nlp_utils import extract_preferences

router = APIRouter()

def construct_prompt(user_query: str, menu_items: list, restaurant_info: dict, preferences: dict):
    prompt = f"""
    User Query: {user_query}
    Extracted Preferences: {preferences}
    Restaurant: {restaurant_info['name']}
    Cuisine: {', '.join(restaurant_info['cuisine'])}

    Menu Items:
    {'-' * 40}
    """
    for item in menu_items:
        prompt += f"\n{item['name']} - ${item['price']}\n{item['description']}\n"

    prompt += f"\n{'-' * 40}\nBased on the user's query, extracted preferences, and the menu items provided, recommend up to 3 dishes. Explain why each dish is recommended."

    return prompt

def get_mock_recommendation(query: str):
    query = query.lower()
    if "vegetarian" in query:
        return "I recommend trying our Vegetarian Lasagna. It's a delicious dish with layers of pasta, seasonal vegetables, and a rich tomato sauce. It's perfect for vegetarians and packed with flavor!"
    elif "fish" in query or "seafood" in query:
        return "Our Grilled Salmon is an excellent choice. It's a fresh salmon fillet grilled to perfection and served with a delightful lemon butter sauce. It's one of our most popular seafood dishes!"
    elif "pasta" in query or "italian" in query:
        return "You can't go wrong with our Spaghetti Carbonara. It's a classic Italian pasta dish made with eggs, cheese, and pancetta. It's creamy, savory, and absolutely delicious!"
    elif "dessert" in query or "sweet" in query:
        return "For dessert, I highly recommend our Tiramisu. It's a traditional Italian dessert with coffee-soaked ladyfingers and creamy mascarpone. It's the perfect sweet ending to your meal!"
    else:
        return "Based on our current popular dishes, I'd recommend trying our Grilled Salmon. It's fresh, healthy, and comes with a delicious lemon butter sauce. If you're in the mood for pasta, our Spaghetti Carbonara is also a fantastic choice!"

@router.post("/api/chat/{restaurant_id}")
async def chat_recommendation(restaurant_id: str, chat_message: ChatMessage):
    # Extract preferences from the user's message
    # preferences = extract_preferences(chat_message.message)
    #
    # # Fetch restaurant info
    # restaurant = await db.restaurants.find_one({"_id": restaurant_id})
    # if not restaurant:
    #     raise HTTPException(status_code=404, detail="Restaurant not found")
    #
    # # Filter menu based on extracted preferences
    # filtered_menu = await filter_menu(restaurant_id, preferences)
    #
    # # Construct prompt for Ollama
    # prompt = construct_prompt(chat_message.message, filtered_menu, restaurant, preferences)
    #
    # # Get recommendation from Ollama
    # ai_response = await get_ollama_response(prompt)
    restaurant_id = ObjectId(restaurant_id)
    print(restaurant_id)
    restaurant = await db.restaurants.find_one({"_id": restaurant_id})
    print(restaurant)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Get mock recommendation
    recommendation = get_mock_recommendation(chat_message.message)
    # Format and return the response
    return {
        "text": recommendation,
        "sender": "bot"
    }

@router.get("/api/ai-prompts/{restaurant_id}")
async def get_ai_prompts(restaurant_id: str):
    restaurant_id = ObjectId(restaurant_id)
    restaurant = await db.restaurants.find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Fetch AI prompts from the restaurant document
    ai_prompts = restaurant.get('ai_prompts')
    print(restaurant)

    # If no prompts are found in the restaurant document, use default prompts
    if not ai_prompts:
        ai_prompts = [
            "What do you suggest for a light meal?",
            "What's good for someone who likes spicy food?",
            "Can you recommend a vegetarian option?",
            "What's your most popular dish?",
            "What's a good choice for a quick bite?"
        ]

    return ai_prompts