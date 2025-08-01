from sqlalchemy import Integer, Boolean, Column, String, Table, MetaData,DateTime
from sqlalchemy.ext.declarative import declarative_base

from tools.database import Base

class User(Base):
  __tablename__ = "users"
  
  id = Column(Integer, autoincrement=True,primary_key=True)
  username = Column(String(32),unique=True,comment="用户名")
  password = Column(String(256), comment="密码")
  full_name = Column(String(16),index=True, comment="姓名")
  email = Column(String(32), comment="邮箱")
  mobile = Column(String(11), comment="手机号")
  status = Column(Integer, default=1, comment="状态")
  create_time = Column(DateTime, comment="创建时间")
