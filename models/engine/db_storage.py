#!/usr/bin/python3
"""
Contains the class DBStorage using SQLite
"""

import models
from models.base_model import BaseModel, Base
from models.user import User
from models.batch import Batch
from models.waste import Waste
from models.harvest import Harvest_log
from models.monitoring import Monitoring_log
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError
from os import getenv
from dotenv import load_dotenv
import time

classes = {"Batch": Batch, "Waste": Waste, "Harvest_log": Harvest_log, "User": User, "Monitoring_log": Monitoring_log}

load_dotenv()

class DBStorage:
    """interacts with the SQLite database"""
    __engine = None
    __session = None

    def __init__(self):
        # 1. Get the Database Type (mysql or sqlite)
        DB_TYPE = getenv('DB_TYPE', 'sqlite')
        DB = getenv('DB', 'hbnb_dev.db')
        
        if DB_TYPE == 'mysql':
            # 2. Pull variables passed from docker-compose
            USER = getenv('MYSQL_USER')
            PWD = getenv('MYSQL_PASSWORD')
            HOST = getenv('MYSQL_HOST', 'db')
            DB = getenv('MYSQL_DB') # This maps to MYSQL_DATABASE in .env
            
            # 3. Defensive check to prevent AssertionErrors
            if not all([USER, PWD, DB]):
                raise ValueError("Missing database environment variables!")

            # 4. Construct the Connection URL
            url = 'mysql+pymysql://{}:{}@{}/{}'.format(USER, PWD, HOST, DB)
            
            # 5. Initialize the Engine
            self.__engine = create_engine(url, pool_pre_ping=True, # check if connection is alive
                                          pool_size=10, # maintain 10 connections
                                          max_overflow=20, # Allow 20 extra if needed
                                          pool_recycle=3600) # refresh connections every hour.
        else:
            self.__engine = create_engine(f'sqlite:///{DB}')

    def all(self, cls=None, limit=None, offset=None):
        """Enhanced query with pagination support"""
        new_dict = {}
        if cls:
            # Determine the class
            target_cls = classes[cls] if isinstance(cls, str) else cls
            
            # Optimize query: Use limit/offset for pagination
            query = self.__session.query(target_cls)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            objs = query.all()
            for obj in objs:
                key = "{}.{}".format(obj.__class__.__name__, obj.id)
                new_dict[key] = obj
        else:
            # Warning: This is still heavy, but we can't paginate across multiple tables easily
            for clss_obj in classes.values():
                objs = self.__session.query(clss_obj).all()
                for obj in objs:
                    key = "{}.{}".format(obj.__class__.__name__, obj.id)
                    new_dict[key] = obj
        return new_dict

    def new(self, obj):
        """add the object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """commit all changes of the current database session"""
        try:
            self.__session.commit()
            return 0
        except IntegrityError:
            self.__session.rollback()
            return 1

    def delete(self, obj=None):
        """delete from the current database session obj if not None"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Creates all tables in the database with a connection retry loop"""
        retries = 10  # Increased to 10 to give MySQL plenty of time to warm up
        connected = False

        while retries > 0:
            try:
                # Try to connect and create tables in one go
                Base.metadata.create_all(self.__engine)
                print("Successfully connected and synced database tables!")
                connected = True
                break
            except OperationalError as e:
                retries -= 1
                if retries == 0:
                    print("Final attempt failed. Could not connect to the database.")
                    raise e  # Crash gracefully after all attempts fail
                
                print(f"Database not ready. Retrying in 5s... ({retries} attempts left)")
                time.sleep(5)

        if connected:
            # Only initialize the session if the connection succeeded
            sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
            Session = scoped_session(sess_factory)
            self.__session = Session

    def close(self):
        """call remove() method on the private session attribute"""
        self.__session.remove()

    def get(self, cls, id):
        """
        Returns the object based on the class and its ID
        """
        if cls not in classes.values() and cls not in classes:
            return None

        # Determine the correct class object
        target_cls = classes[cls] if type(cls) is str else cls
        
        # Querying directly is more efficient than calling all()
        return self.__session.query(target_cls).filter_by(id=id).first()

    def count(self, cls=None):
        """
        count the number of objects in storage
        """
        if not cls:
            count = 0
            for clss_obj in classes.values():
                count += self.__session.query(clss_obj).count()
        else:
            target_cls = classes[cls] if type(cls) is str else cls
            count = self.__session.query(target_cls).count()

        return count
 
    def get_session(self):
        """Returns the current database session"""
        return self.__session
