from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional,Annotated, List
from sqlalchemy.orm import Session
from middlerware.middle_auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from tools.database import get_db
from models.usermodel import User
from passlib.context import CryptContext
from datetime import datetime

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/api/user")


class LoginFormModel(BaseModel):
    username:str = Field(...,description="用户名")
    password:str = Field(...,description="密码")

class RegisterFormModel(BaseModel):
    username:str = Field(...,description="用户名")
    password:str = Field(...,description="密码")
    email:Optional[str] = Field(...,description="邮箱")

class ChangeModel(BaseModel):
    username:str = Field(...,description="用户名")
    password:str = Field(...,description="旧密码")
    new_password:str = Field(...,description="新密码")

class UserInfoModel(BaseModel):
    id:int = Field(...,description="用户id")
    username:str = Field(...,description="用户名")
    password:str = Field(...,description="密码")
    full_name:Optional[str|None] = Field(...,description="姓名")
    mobile:Optional[str] = Field(...,description="手机号")
    email:Optional[str] = Field(...,description="邮箱")
    status:int = Field(...,description="状态")
    create_time:datetime = Field(...,description="创建时间")

class FilterParams(BaseModel):
    id:Optional[int|None] = Field(...,description="用户id")
    username:Optional[str|None] = Field(...,description="用户名")
    full_name:Optional[str|None] = Field(...,description="姓名")
    email:Optional[str|None] = Field(...,description="邮箱")
    status:Optional[int|None] = Field(...,description="状态")
    mobile:Optional[str|None] = Field(...,description="手机号")
    

class ResponseModel(BaseModel):
    msg:str = Field(...,description="信息")
    code:int = Field(...,description="状态码")
    
class TokenModel(ResponseModel):
    data: str = Field(..., description="访问令牌")

class DetailModel(ResponseModel):
    data:Optional[List[UserInfoModel]|None] = Field(...,description="数据")
    count:Optional[int|None] = Field(...,description="数量")


class UserUpdateModel(BaseModel):
    id:int = Field(...,description="用户id")
    password:Optional[str] = Field(...,description="密码")
    full_name:Optional[str] = Field(...,description="姓名")
    mobile:Optional[str] = Field(...,description="手机号")
    email:Optional[str] = Field(...,description="邮箱")
    status:Optional[int] = Field(...,description="状态")
    
class UserDeleteModel(BaseModel):
    id:int = Field(...,description="用户id")
    
@router.post("/login",response_model=TokenModel,tags=["用户"],summary="登录")
async def login(data:LoginFormModel,db:Session = Depends(get_db)):
    try:
        user = authenticate_user(db, data.username, data.password)
        if user is not None:
            # 生成jwt token
            access_token = create_access_token(
                data={"sub": data.username}
            )
            return {"code": 200, "data":access_token,"msg":"登录成功"}
        else:
            return {"code": 0, "msg":"用户名或密码错误"}
    except Exception as e:
        raise HTTPException(status_code=400,detail={"code": 0, "msg":"登录失败"},data=None)


@router.post("/logout",response_model=ResponseModel,tags=["用户"],summary="注销")
async def logout(current_user: Annotated[User, Depends(get_current_active_user)]):
    pass

@router.post("/register",response_model=ResponseModel,tags=["用户"],summary="注册")
async def register(data:RegisterFormModel,db:Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == data.username).first()
        if user:
            raise HTTPException(status_code=400,detail="注册失败，此用户名已存在")
        else:
            new_user = User()
            new_user.username = data.username
            new_user.password = get_password_hash(data.password)
            new_user.email = data.email
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return {"code": 200,"msg":"注册成功"}
    except Exception as e:
        print(e)
        return {"code": 0,"msg":"注册失败"}
    
@router.post("/change",response_model=ResponseModel,tags=["用户"],summary="修改密码")
async def change(data:ChangeModel):
    pass

@router.get("/get",response_model=DetailModel,tags=["用户"],summary="查询用户信息")
async def get(_: Annotated[User, Depends(get_current_active_user)],page:int = 1, limit:int=10,db:Session = Depends(get_db),filters:FilterParams = Depends()):
    try:
        valid_filters = {k: v for k, v in filters.model_dump().items() if v is not None}
        user = db.query(User)
        for k, v in valid_filters.items():
            if not hasattr(User, k):
                user.filter(getattr(User,k)==v)
                

        if id:
            user = db.query(User).filter(User.id==id).offset((page-1)*limit).limit(limit).all()
            count = db.query(User).filter(User.id==id).count()
        else:
            user = db.query(User).offset((page-1)*limit).limit(limit).all()
            count = db.query(User).count()

        if not user:
            return {"code":200,"msg":"查询成功","data":user,"count":count}
        return {"code":200,"msg":"查询成功","data":user,"count":count}
    except Exception:
        raise HTTPException(status_code=400,detail="查询失败")

@router.post("/delete",response_model=ResponseModel,tags=["用户"],summary="删除用户")
async def delete(_: Annotated[User, Depends(get_current_active_user)],data:UserDeleteModel):
    try:
        pass
    except Exception:
        raise HTTPException(status_code=400,detail="删除失败")

@router.post("/update",response_model=ResponseModel,tags=["用户"],summary="修改用户信息")
async def update(_: Annotated[User, Depends(get_current_active_user)],data:UserUpdateModel):
    try:
        pass
    except Exception:
        raise HTTPException(status_code=400,detail="修改失败")