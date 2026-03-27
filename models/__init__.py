#!/usr/bin/python3
"""
initialize the models package
"""


from models.engine.db_storage import DBStorage
import time
from sqlalchemy.exc import OperationalError
storage = DBStorage()
storage.reload()

def init_db():
    """Retry logic for database connection"""
    retries = 10
    while retries > 0:
        try:
            storage.reload()
            print("Database initialized successfully.")
            return
        except OperationalError:
            retries -= 1
            print(f"Database not ready. Retrying in 5s... ({retries} left)")
            time.sleep(5)
    raise Exception("Database connection failed after multiple retries.")

# You can call this explicitly in your app.py before the server starts
