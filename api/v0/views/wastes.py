#!/usr/bin/python3
from flask import jsonify, abort, request, make_response
from models import storage
from models.user import User
from models.waste import Waste
from api.v0.views import app_views
from flasgger.utils import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

@app_views.route('/wastes', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/wastes/get_wastes.yml')
def get_wastes():
    """ Retrieves the list of all waste sources """
    current_user = get_jwt_identity()
    user = storage.get(User, current_user)
    if not user:
        abort(404)
    if user.user_type != 'admin':
        abort(409, description='Insufficient permissions')

    all_wastes = [obj.to_dict() for obj in storage.all(Waste).values()]
    return jsonify(all_wastes)

@app_views.route('/wastes/<waste_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/wastes/get_waste.yml')
def get_waste(waste_id):
    """ Retrieves a specific waste object """
    waste = storage.get(Waste, waste_id)
    if not waste:
        abort(404)
    return jsonify(waste.to_dict())

@app_views.route('/wastes', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/wastes/post_waste.yml')
def post_waste():
    """ Creates a new waste record """
    if not request.get_json():
        abort(400, description="Not a JSON")
    
    data = request.get_json()

    if 'arrival_date' in data and isinstance(data['arrival_date'], str):
        try:
            # Converts "YYYY-MM-DD" string to a Python date object
            data['arrival_date'] = datetime.strptime(data['arrival_date'], '%Y-%m-%d').date()
        except ValueError:
            abort(400, description="Invalid date format. Use YYYY-MM-DD")

    if 'source_location' not in data:
        abort(400, description="Missing source_location")
    if 'quantity_kg' not in data:
        abort(400, description="Missing quantity_kg")

    instance = Waste(**data)
    if instance.save() == 0:
        return make_response(jsonify(instance.to_dict()), 201)
    abort(409)

@app_views.route('/wastes/<waste_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/wastes/put_waste.yml')
def put_waste(waste_id):
    """ Updates a waste record """
    waste = storage.get(Waste, waste_id)
    if not waste:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    ignore = ['id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore:
            setattr(waste, key, value)
    
    if storage.save() == 0:
        return jsonify(waste.to_dict()), 200
    abort(409)

@app_views.route('/wastes/<waste_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/wastes/delete_waste.yml')
def delete_waste(waste_id):
    """ Deletes a waste record """
    waste = storage.get(Waste, waste_id)
    if not waste:
        abort(404)
    
    storage.delete(waste)
    storage.save()
    return make_response(jsonify({}), 200)
