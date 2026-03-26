#!/usr/bin/python3
""" holds class Batch"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Date, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime


class Monitoring_log(BaseModel, Base):
    """Representation of monitoring model for eggs development"""
    __tablename__ = 'monitoring_logs'
    temp = Column(Float)
    humidity = Column(Float)
    larvae_density = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(60), ForeignKey('batches.id'), nullable=False)
