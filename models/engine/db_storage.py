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
from sqlalchemy.exc import IntegrityError
from os import getenv
from dotenv import load_dotenv

classes = {"Batch": Batch, "Waste": Waste, "Harvest_log": Harvest_log, "User": User, "Monitoring_log": Monitoring_log}

load_dotenv()

class DBStorage:
    """interacts with the SQLite database"""
    __engine = None
    __session = None

    def __init__(self):
        # Default to 'hbnb_dev.db' if no name is provided in env
        DB_NAME = getenv('HBNB_SQLITE_DB', 'hbnb_dev.db')
        #HBNB_ENV = getenv('HBNB_ENV')
        #DB_STRING = getenv('DB_URL') # SQLite connection string: sqlite:///path/to/db
        self.__engine = create_engine('sqlite:///{}'.format(DB_NAME), pool_pre_ping=True)
        # Use connect_args to force SSL and avoid the 'argument 18' string/bool error
        #self.__engine = create_engine(
        #                              pool_pre_ping=True)
        #    connect_args={
        #        "ssl_verify_cert": True,
        #        "ssl_verify_identity": True,
        #        "ssl_ca": "/etc/ssl/certs/ca-certificates.crt"
        #    },
        #    pool_pre_ping=True
        #)

        #if HBNB_ENV == 'test':
        #    Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """query on the current database session"""
        new_dict = {}
        for clss_name, clss_obj in classes.items():
            if cls is None or cls is clss_obj or cls == clss_name:
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
        """reloads data from the database"""
        Base.metadata.create_all(self.__engine)
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
