#!/usr/bin/python3
"""
Declare enums used in database
"""

class UserType(enum.Enum):
    """Declare an enum class for the user types"""
    REGULAR = 'regular'
    ADMIN = 'admin'
