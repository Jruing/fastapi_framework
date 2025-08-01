from datetime import datetime, timedelta
import os
from typing import Annotated, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models.usermodel import User
from tools.database import get_db
load_dotenv(".env")
SECRET_KEY = os.getenv("SECRET_KEY")
# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 令牌获取方式（从请求头的 Authorization: Bearer <token> 中提取）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_user(db: Session, username:str)-> Optional[User]:
    """根据用户名查找用户信息"""
    return db.query(User).filter(User.username == username,User.status == 1).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否正确"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户身份（用户名和密码）"""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    依赖项：验证令牌并返回当前用户
    若令牌无效或用户不存在，抛出 401 错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")  # "sub" 是 JWT 标准中的主题字段
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # 获取用户
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    依赖项：验证当前用户是否为活跃状态
    可在需要时添加额外的状态检查（如账号是否被封禁）
    """
    if not current_user:
        raise HTTPException(status_code=400, detail="非活跃用户")
    return current_user