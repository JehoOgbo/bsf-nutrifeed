#!/usr/bin/python3
from flask import jsonify, abort, request, make_response
from models import storage
from models.monitoring import Monitoring_log
from models.batch import Batch
from api.v0.views import app_views
from flasgger.utils import swag_from
from flask_jwt_extended import jwt_required
from models.engine.cache import cache
import json

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

    # ------------------------
    # NOTE: Check redis first for quicker query times
    cache_key = "all_monitoring_logs"

    # 1. Check if the full log list is in Redis
    cached_logs = cache.get(cache_key)
    if cached_logs:
        return jsonify(json.loads(cached_logs))

    # 2. Cache Miss: Pull from MySQL
    all_logs = [obj.to_dict() for obj in storage.all(Monitoring_log).values()]

    # 3. Save to Redis (Expire in 300s since logs change frequently)
    # We use a shorter expiration here because admin logs need to be relatively fresh
    cache.setex(cache_key, 300, json.dumps(all_logs))
    # --- REDIS INTEGRATION END ---

    return jsonify(all_logs)

#@app_views.route('/batches/<batch_id>/logs', methods=['GET'], strict_slashes=False)
#@jwt_required()
#@swag_from('documentation/monitoring/get_logs.yml')
#def get_monitoring_logs(batch_id):
#    """ Retrieves all monitoring logs for a specific batch """
#    batch = storage.get(Batch, batch_id)
#    if not batch:
#        abort(404, description="Batch not found")
    
#    logs = [log.to_dict() for log in batch.monitoring_logs]
#    return jsonify(logs)

@app_views.route('/batches/<batch_id>/logs', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/monitoring/get_logs.yml')
def get_monitoring_logs(batch_id):
    """ Retrieves all monitoring logs for a specific batch with Redis Caching """
    
    # 1. Define a batch-specific cache key
    cache_key = f"logs_batch_{batch_id}"
    
    # 2. Check Redis first
    cached_logs = cache.get(cache_key)
    if cached_logs:
        return jsonify(json.loads(cached_logs))

    # 3. Cache Miss: Query MySQL
    batch = storage.get(Batch, batch_id)
    if not batch:
        abort(404, description="Batch not found")
    
    logs = [log.to_dict() for log in batch.monitoring_logs]

    # 4. Save to Redis (Expire in 10 minutes / 600s)
    # This provides a good balance between speed and data freshness
    cache.setex(cache_key, 600, json.dumps(logs))
    
    return jsonify(logs)

#@app_views.route('/batches/<batch_id>/logs', methods=['POST'], strict_slashes=False)
#@jwt_required()
#@swag_from('documentation/monitoring/post_log.yml')
#def post_monitoring_log(batch_id):
#    """ Creates a new environmental monitoring log for a batch """
#    batch = storage.get(Batch, batch_id)
#    if not batch:
#        abort(404, description="Batch not found")
#        
#    if not request.get_json():
#        abort(400, description="Not a JSON")
#    
#    data = request.get_json()
#    data['batch_id'] = batch_id
#    
#    instance = Monitoring_log(**data)
#    if instance.save() == 0:
#        return make_response(jsonify(instance.to_dict()), 201)
#    abort(409)

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
    temp = data.get('temp')
    humidity = data.get('humidity')

    if temp is not None and (temp < 0 or temp > 100):
        return jsonify({"error": "Invalid temperature range"}), 400

    if humidity is not None and (humidity < 0 or humidity > 100):
        return jsonify({"error": "Humidity must be between 0 and 100"}), 400

    instance = Monitoring_log(**data)
    if instance.save() == 0:
        # --- CACHE INVALIDATION START ---
        # 1. Delete the specific batch log list cache
        cache.delete(f"logs_batch_{batch_id}")


        # 2. Delete the global admin logs cache
        cache.delete("all_monitoring_logs")
        # --- CACHE INVALIDATION END ---

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

#@app_views.route('/batches/<batch_id>/logs', methods=['GET'], strict_slashes=False)
#@jwt_required()
#@swag_from('documentation/monitoring/get_batch_logs.yml')
#def get_batch_logs(batch_id):
#    """ Retrieves all monitoring logs associated with a specific batch """
#    batch = storage.get(Batch, batch_id)
#    if not batch:
#        abort(404, description="Batch not found")
    
    # Accessing logs via the relationship defined in Batch model
#    logs = [log.to_dict() for log in batch.monitoring_logs]
#    return jsonify(logs)

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
