#!/usr/bin/python3
"""holds user class"""
import models
# from models.enum import UserType
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import os
import shutil
from uuid import uuid4



class User(BaseModel, Base):
    """Representation of the Sender"""
    __tablename__ = 'users'
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, unique=True)
    password = Column(String(1024), nullable=False)
    user_type = Column(Enum(UserType), default=UserType.REGULAR,
                       nullable=False)
    batches = relationship("Batch", backref='user',
                         cascade='all, delete, delete-orphan')
