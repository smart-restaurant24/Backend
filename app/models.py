from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str

class MenuItem(BaseModel):
    name: str
    description: str
    price: float
    image: str

class Recommendation(BaseModel):
    name: str
    description: str
    price: float
    image: str
    score: float