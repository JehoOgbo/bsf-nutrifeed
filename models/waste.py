#!/usr/bin/python3
"""holds waste_source class"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Enum, Date, Float
from sqlalchemy.orm import relationship
import os



class Waste(BaseModel, Base):
    """Representation of the Sender"""
    __tablename__ = 'wastes'
    source_location = Column(String(128), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    arrival_date = Column(Date, nullable=False)
    batches = relationship("Batch", backref='waste',
                         cascade='all, delete, delete-orphan')
