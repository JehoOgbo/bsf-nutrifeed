#!/usr/bin/python3
""" holds class Batch"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Date
from sqlalchemy.orm import relationship


class Batch(BaseModel, Base):
    """Representation of batch model """
    __tablename__ = 'batches'
    name = Column(String(60), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    source_id = Column(String(60), ForeignKey('wastes.id'), nullable=False)
    shredded_weight = Column(Float)
    moisture_content = Column(Float)
    monitoring_logs = relationship("Monitoring_log", backref='batch',
                                   cascade='all, delete, delete-orphan')
    harvest_logs = relationship("Harvest_log", backref='batch',
                                cascade='all, delete, delete-orphan')
