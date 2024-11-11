from fastapi import FastAPI, HTTPException
from app.routers.auth_router import router as auth_router
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from contextlib import asynccontextmanager
from app.bot.bot_router import router as bot_router
from app.bot.bot_chat import router as query_router


def create_tables():
    from app.models import user_model, chat_model
    Base.metadata.create_all(engine)
    logging.info("Database Tables Created Successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
    except Exception as e:
        logging.error(f"Failed to connect to the database: {e}")
    yield

app = FastAPI(lifespan=lifespan)
# Include the authentication router
app.include_router(auth_router, tags=['User'])
app.include_router(bot_router, tags=['Bot'])
app.include_router(query_router, tags=['Query'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



origins = [
    'http://localhost:3000',
]
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    try:
        return {"message": "HAsteAI backend is running"}
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
