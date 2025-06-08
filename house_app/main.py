import fastapi
from house_app.db.database import engine
import uvicorn
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from sqladmin import Admin
from house_app.api import auth, house_path
from starlette.middleware.sessions import SessionMiddleware
from house_app.config import SECRET_KEY

async def init_redis():
    return redis.Redis.from_url('redis://localhost', encoding='utf-8', decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    await FastAPILimiter.init(redis)
    yield
    await redis.close()

house = fastapi.FastAPI(title='House_KG', lifespan=lifespan)
house.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")

admin = Admin(house, engine)

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

house.include_router(auth.auth_router)
house.include_router(house_path.house_router)

if __name__ == "__main__":
    uvicorn.run(house, host="127.0.0.1", port=8001)
 
