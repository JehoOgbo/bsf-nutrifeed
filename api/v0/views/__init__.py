#!/usr/bin/python3
""" Blueprint for API """
from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v0')

from api.v0.views.users import *
from api.v0.views.batches import *
from api.v0.views.harvest_logs import *
from api.v0.views.monitoring_logs import *
from api.v0.views.wastes import *
from api.v0.views.signin import *
