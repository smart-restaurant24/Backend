from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import menu, chat, recommendation
from .database import init_db

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://hardcore_jemison:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(menu.router)
app.include_router(chat.router)
app.include_router(recommendation.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)