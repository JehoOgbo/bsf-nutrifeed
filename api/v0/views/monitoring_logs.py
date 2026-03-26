from flask import jsonify, abort, request, make_response
from models import storage
from models.monitoring import Monitoring_log
from models.batch import Batch
from api.v0.views import app_views
from flasgger.utils import swag_from
from flask_jwt_extended import jwt_required

@app_views.route('/logs', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/get_all_logs.yml')
def get_logs():
    """ Retrieves all logs """
    current_user = get_jwt_identity()
    user = storage.get(User, current_user)
    if not user:
        abort(404)
    if user.user_type != 'admin':
        abort(409, description='Insufficient permissions')

    all_logs = [obj.to_dict() for obj in storage.all(Monitoring_log).values()]
    return jsonify(all_logs)

@app_views.route('/batches/<batch_id>/logs', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/get_logs.yml')
def get_monitoring_logs(batch_id):
    """ Retrieves all monitoring logs for a specific batch """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404, description="Batch not found")
    
    logs = [log.to_dict() for log in batch.monitoring_logs]
    return jsonify(logs)

@app_views.route('/batches/<batch_id>/logs', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/post_log.yml')
def post_monitoring_log(batch_id):
    """ Creates a new environmental monitoring log for a batch """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404, description="Batch not found")
        
    if not request.get_json():
        abort(400, description="Not a JSON")
    
    data = request.get_json()
    data['batch_id'] = batch_id
    
    instance = Monitoring_log(**data)
    if instance.save() == 0:
        return make_response(jsonify(instance.to_dict()), 201)
    abort(409)

@app_views.route('/logs/<log_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/delete_log.yml')
def delete_monitoring_log(log_id):
    """ Deletes a specific monitoring log """
    log = storage.get(Monitoring_log, log_id)
    if not log:
        abort(404)
    
    storage.delete(log)
    storage.save()
    return make_response(jsonify({}), 200)

@app_views.route('/batches/<batch_id>/logs', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/get_batch_logs.yml')
def get_batch_logs(batch_id):
    """ Retrieves all monitoring logs associated with a specific batch """
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404, description="Batch not found")
    
    # Accessing logs via the relationship defined in Batch model
    logs = [log.to_dict() for log in batch.monitoring_logs]
    return jsonify(logs)

@app_views.route('/logs/<log_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/get_log.yml')
def get_monitoring_log(log_id):
    """ Retrieves a single specific monitoring log """
    log = storage.get(Monitoring_log, log_id)
    if not log:
        abort(404)
    return jsonify(log.to_dict())

@app_views.route('/logs/<log_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/put_log.yml')
def put_monitoring_log(log_id):
    """ Updates an existing monitoring log entry """
    log = storage.get(Monitoring_log, log_id)
    if not log:
        abort(404)
    
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    # Fields that should not be updated manually
    ignore = ['id', 'batch_id', 'created_at', 'updated_at', 'timestamp']
    for key, value in data.items():
        if key not in ignore:
            setattr(log, key, value)
    
    if storage.save() == 0:
        return jsonify(log.to_dict()), 200
    abort(409)
