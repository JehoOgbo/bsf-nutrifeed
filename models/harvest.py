#!/usr/bin/python3
""" holds class Batch"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship


class Harvest_log(BaseModel, Base):
    """Representation of harvest model for monitoring
    larvae development and residue"""
    __tablename__ = 'harvest_logs'
    larvae_weight = Column(Float)
    avg_larvae_size = Column(Float)
    residue_weight = Column(Float)
    residue_frass_grade = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow().time)
    batch_id = Column(String(60), ForeignKey('batches.id'), nullable=False)
