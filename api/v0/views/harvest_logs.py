#!/usr/bin/python3
from flask import jsonify, abort, request, make_response
from models import storage
from models.harvest import Harvest_log
from models.batch import Batch
from api.v0.views import app_views
from flasgger.utils import swag_from
from flask_jwt_extended import jwt_required


@app_views.route('/harvests', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/harvest/get_harvests.yml')
def get_harvests():
    """ Retrieves all harvests """
    current_user = get_jwt_identity()
    user = storage.get(User, current_user)
    if not user:
        abort(404)
    if user.user_type != 'admin':
        abort(409, description='Insufficient permissions')

    all_harvests = [obj.to_dict() for obj in storage.all(Harvest_log).values()]
    return jsonify(all_harvests)


@app_views.route('/batches/<batch_id>/harvest', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/harvest/get_harvest_logs.yml')
def get_harvest_logs(batch_id):
    """ Retrieves all harvest logs for a specific batch """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404, description="Batch not found")
    
    logs = [log.to_dict() for log in batch.harvest_logs]
    return jsonify(logs)

@app_views.route('/batches/<batch_id>/harvest', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/harvest/post_harvest.yml')
def post_harvest_log(batch_id):
    """ Records a harvest event for a batch """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404, description="Batch not found")
        
    if not request.get_json():
        abort(400, description="Not a JSON")
    
    data = request.get_json()
    data['batch_id'] = batch_id
    
    instance = Harvest_log(**data)
    if instance.save() == 0:
        return make_response(jsonify(instance.to_dict()), 201)
    abort(409)

@app_views.route('/harvest/<log_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/harvest/get_harvest.yml')
def get_harvest_log(log_id):
    """ Retrieves a single specific harvest log """
    log = storage.get(Harvest_log, log_id)
    if not log:
        abort(404)
    return jsonify(log.to_dict())

@app_views.route('/harvest/<log_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/harvest/put_harvest.yml')
def put_harvest_log(log_id):
    """ Updates harvest data (e.g. correcting weights) """
    log = storage.get(Harvest_log, log_id)
    if not log:
        abort(404)
    
    data = request.get_json()
    ignore = ['id', 'batch_id', 'created_at', 'updated_at', 'timestamp']
    for key, value in data.items():
        if key not in ignore:
            setattr(log, key, value)
    
    storage.save()
    return jsonify(log.to_dict()), 200

@app_views.route('/harvest/<log_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/harvest/delete_harvest.yml')
def delete_harvest_log(log_id):
    """
    Permanently deletes a specific harvest log
    """
    log = storage.get(Harvest_log, log_id)

    if not log:
        abort(404, description="Harvest log not found")

    storage.delete(log)
    storage.save()

    return make_response(jsonify({}), 200)
