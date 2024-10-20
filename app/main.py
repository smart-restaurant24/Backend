from fastapi import FastAPI ,Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import menu, chat, recommendation
from .database import init_db
import logging
import sys

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
    ]
)

def debug_print(message):
    print(message, flush=True)
    sys.stdout.flush()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    debug_print("Root endpoint called")
    debug_print(f"Received request: {request.method} {request.url}")
    debug_print(f"Headers: {request.headers}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend URL
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