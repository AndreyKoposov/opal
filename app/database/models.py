from sqlalchemy import Column, Integer, String, ForeignKey

from .engine import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class Process(Base):
    __tablename__ = "processes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
