#!/usr/bin/python3
""" Blueprint for API """
from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v0')

from api.v0.views.users import *
# from api.v0.views.index import *
# from api.v0.views.exams import *
# from api.v0.views.questions import *
# from api.v0.views.options import *
# from api.v0.views.signin import *
# from api.v0.views.sections import *
# from api.v0.views.pdf import *
