from flask import jsonify, abort, request, make_response
from models import storage
from models.batch import Batch
from api.v0.views import app_views
from flasgger.utils import swag_from
from models.user import User
from models.waste import Waste
from flask_jwt_extended import jwt_required, get_jwt_identity

@app_views.route('/batches', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/batches/get_batches.yml')
def get_batches():
    """ Retrieves all batches """
    current_user = get_jwt_identity()
    user = storage.get(User, current_user)
    if not user:
        abort(404)
    if user.user_type != 'admin':
        abort(409, description='Insufficient permissions')

    all_batches = [obj.to_dict() for obj in storage.all(Batch).values()]
    return jsonify(all_batches)

@app_views.route('/batches/<batch_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/batches/get_batch.yml')
def get_batch(batch_id):
    """ Retrieves a specific batch """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404)
    return jsonify(batch.to_dict())

@app_views.route('/waste/<source_id>/batches', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/batches/post_batch.yml')
def post_batch(source_id):
    """ Creates a new production batch """
    if not request.get_json():
        abort(400, description="Not a JSON")

    source = storage.get(Waste, source_id)
    if not source:
        abort(404, description='Waste source not found')
    data = request.get_json()
    # Automatically link the batch to the logged-in user
    data['user_id'] = get_jwt_identity()
    data['source_id'] = source_id

    if 'name' not in data:
        abort(400, description="Missing name")

    instance = Batch(**data)
    if instance.save() == 0:
        return make_response(jsonify(instance.to_dict()), 201)
    abort(409)

@app_views.route('/batches/<batch_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/batches/put_batch.yml')
def put_batch(batch_id):
    """ Updates batch metrics (e.g. after shredding) """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404)
    
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    ignore = ['id', 'user_id', 'source_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore:
            setattr(batch, key, value)
    
    storage.save()
    return jsonify(batch.to_dict()), 200

@app_views.route('/batches/<batch_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/batches/delete_batch.yml')
def delete_batch(batch_id):
    """ Deletes a batch record """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404)
    
    storage.delete(batch)
    storage.save()
    return make_response(jsonify({}), 200)

@app_views.route('/users/<user_id>/batches', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/batches/get_user_batches.yml')
def get_user_batches(user_id):
    """
    Retrieves the list of all Batch objects belonging to a user
    """
    user = storage.get(User, user_id)
    if not user:
        abort(404, description="User not found")
    
    # Using the 'batches' relationship defined in your User model
    list_batches = [batch.to_dict() for batch in user.batches]
    return jsonify(list_batches)

@app_views.route('/wastes/<waste_id>/batches', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/batches/get_waste_batches.yml')
def get_waste_batches(waste_id):
    """
    Retrieves all batches that were started using a specific waste source
    """
    waste = storage.get(Waste, waste_id)
    if not waste:
        abort(404, description="Waste source not found")
    
    # Using the 'batches' relationship defined in your Waste model
    list_batches = [batch.to_dict() for batch in waste.batches]
    return jsonify(list_batches)
