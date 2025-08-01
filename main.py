# 创建数据库表
from fastapi import FastAPI
from tools.database import Base,engine
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    user
)
import models.usermodel
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("创建表")
    yield # 在with语句中执行
    
app = FastAPI(title="Python",description="Python学习",lifespan=lifespan)
app.include_router(router=user.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='main:app',host="127.0.0.1",port=8002)