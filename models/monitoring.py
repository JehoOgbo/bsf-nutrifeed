#!/usr/bin/python3
""" holds class Batch"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship


class Monitoring_log(BaseModel, Base):
    """Representation of batch model """
    __tablename__ = 'batches'
    temp = Column(Float)
    humidity = Column(Float)
    larvae_density = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow().time)
    name = Column(String(60), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    source_id = Column(String(60), ForeignKey('wastes.id'), nullable=False)
    shredded_weight = Column(Float)
    moisture_content = Column(Float)
