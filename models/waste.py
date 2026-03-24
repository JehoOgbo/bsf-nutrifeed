#!/usr/bin/python3
"""holds waste_source class"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import os



class Waste(BaseModel, Base):
    """Representation of the Sender"""
    __tablename__ = 'waste'
    source_location = Column(String(128), nullable=False)
    quantity_kg = Column(String(128), nullable=False, unique=True)
    arrival_date = Column(Date)
    shredded_weight = Column(Float)
    moisture_content = Column(Float)
    batches = relationship("Batch", backref='waste',
                         cascade='all, delete, delete-orphan')
