#!/usr/bin/python3
""" Flask Application """
from models import storage
from api.v0.views import app_views
from os import environ
from flask import Flask, render_template, make_response, jsonify
from flask_cors import CORS
from flasgger import Swagger
from flasgger.utils import swag_from
from flask_jwt_extended import JWTManager
from uuid import uuid4
from datetime import timedelta
import os
from flask import request, redirect, url_for
import yaml
# from api.v0.views.documentation.definitions import schema_definitions # Import here

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/api/v0/*": {"origins": "*"}})
# UPLOAD_FOLDER = 'uploads'

# -- UPLOAD Configuration --
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -- JWT Configuration --
# You should generate a complex, random key for production
app.config["JWT_SECRET_KEY"] = str(uuid4())
# Set the token expiration time
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)


@app.teardown_appcontext
def close_db(error):
    """ Close Storage """
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """404 Error
    ---
    responses:
        404:
            description: a resourse was not found
    """
    return make_response(jsonify({'error': "Not found"}), 404)

@app.errorhandler(400)
def bad_req(error):
    """ 400 error
    ---
    responses:
    400:
        description: This is a bad request.
    """
    return make_response(jsonify({'error': "This is a bad request"}), 409)

@app.errorhandler(409)
def conflict(error):
    """409 Error
    ---
    responses:
    409:
        description: a conflict occured. Possible duplicate
    """
    return make_response(jsonify({'error': "Duplicate Entry. Name already exists"}), 409)

with open('api/v0/views/documentation/definitions.yml', 'r') as f:
    external_definitions = yaml.safe_load(f)
# Security configuration for Swagger
template = {
    "swagger": "2.0",
    "info": {
        "title": "BSF-NutriFeed API",
        "description": "API for Black Soldier Fly Larvae Production Tracking",
        "version": "1.0.1"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    }
}

template['definitions'] = external_definitions
    #"definitions": schema_definitions
#}

app.config['SWAGGER'] = {
    'title': 'BSF-NutriFeed API',
    'uiversion': 3
}

swagger = Swagger(app, template=template)

if __name__ == "__main__":
    """ Main Function """
    host = environ.get('BSF_HOST')
    port = environ.get('BSF_PORT')
    if not host:
        host = '0.0.0.0'
    if not port:
        port = '5050'
    app.run(host=host, port=port, threaded=True)
