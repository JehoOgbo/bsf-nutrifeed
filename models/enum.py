#!/usr/bin/python3
"""
Declare enums used in database
"""
import enum

class UserType(str, enum.Enum):
    """Declare an enum class for the user types"""
    FARMER = 'farmer'
    ADMIN = 'admin'
