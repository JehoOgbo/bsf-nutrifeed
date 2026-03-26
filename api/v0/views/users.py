#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Users """
from models.user import User
from models import storage
from api.v0.views import app_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from flask_jwt_extended import get_jwt_identity
import os
from uuid import uuid4
import logging
from email_validator import validate_email, EmailNotValidError


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app_views.route('/users', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/users/all_users.yml')
def get_users():
    """
    Retrieves the list of all user objects
    or a specific user
    """
    current_user = get_jwt_identity()
    user = storage.get(User, current_user)
    if not user:
        abort(404)
    if user.user_type != 'admin':
        abort(409, description='Insufficient permissions')
    all_users = storage.all(User).values()
    list_users = []
    for users in all_users:
        list_users.append(users.to_dict())
    return jsonify(list_users)


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/users/get_user.yml', methods=['GET'])
def get_user(user_id):
    """ Retrieves an user """
    user = storage.get(User, user_id)
    if not user:
        abort(404)

    return jsonify(user.to_dict())


@app_views.route('/users/<user_id>', methods=['DELETE'],
                 strict_slashes=False)
@jwt_required()
@swag_from('documentation/users/delete_user.yml', methods=['DELETE'])
def delete_user(user_id):
    """
    Deletes a user Object
    """

    user = storage.get(User, user_id)

    if not user:
        abort(404)

    storage.delete(user)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/users', methods=['POST'], strict_slashes=False)
@swag_from('documentation/users/post_user.yml', methods=['POST'])
def post_user():
    """
    Creates a user
    """
    if not request.get_json():
        abort(400, description="Not a JSON")


    if 'name' not in request.get_json():
        abort(400, description="Missing name")
    if 'email' not in request.get_json():
        abort(400, description="Missing email")
    if 'password' not in request.get_json():
        abort(400, description="Missing password")

    data = request.get_json()
    try:
        email_info = validate_email(data.get('email'), check_deliverability=False)
        email = email_info.normalized
    except EmailNotValidError as e:
        abort(400, description=str(e))
    data['password'] = generate_password_hash(data['password'])
    instance = User(**data)
    value = instance.save()
    if value == 0:
        return make_response(jsonify(instance.to_dict()), 201)
    else:
        abort(409)


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/users/put_user.yml', methods=['PUT'])
def put_user(user_id):
    """
    Updates a user
    """
    user = storage.get(User, user_id)

    if not user:
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    ignore = ['id', 'email', 'created_at', 'updated_at', 'image_path', 'password', 'user_type']

    data = request.get_json()
    for key, value in data.items():
        if value == '':
            continue
        if key not in ignore:
            #if key == 'password':
            #    key = generate_password_hash(value)
            setattr(user, key, value)
    value = storage.save()
    if value == 0:
        return make_response(jsonify(user.to_dict()), 200)
    else:
        abort(409)

@app_views.route('/users/<user_id>/pwd', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/users/put_password.yml', methods=['PUT'])
def put_pwd(user_id):
    """ updates the password """
    user = storage.get(User, user_id)

    if not user:
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    old_password = data.get("old_password", None)
    new_password = data.get("new_password", None)

    if check_password_hash(user.password, old_password):
        new_password = generate_password_hash(new_password)
        setattr(user, 'password', new_password)
        value = storage.save()
        if value == 0:
            return make_response(jsonify(user.to_dict()), 200)
        else:
            abort(409)
    return make_response(jsonify({"error": "Incorrect password"}), 401)


def allowed_file(filename: str) -> bool:
    """ Checks if the file has an allowed extension
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app_views.route('/users/upload/<user_id>', methods=['POST'], strict_slashes=False)
def upload_image(user_id):
    """
    Adds image to a user
    """
    UPLOAD_FOLDER = 'front-end/public/uploads/images'
    NEW_UPLOAD_FOLDER = '/uploads/images/'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    user = storage.get(User, user_id)

    if not user:
        abort(404)

    if 'image' not in request.files:
        abort(400, description="Not a File")

    file = request.files['image']

    if file.name == '':
        abort(400, description="No file found")

    if user.image_path:
        delete_name = 'front-end/public' + user.image_path
        if os.path.exists(delete_name):
            os.remove(delete_name)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid4()}{file_ext}"
 
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        file_path = NEW_UPLOAD_FOLDER + unique_filename
        setattr(user, "image_path", file_path)
        setattr(user, "saved_filename", filename)

        value = storage.save()
        if value == 0:
            return make_response(jsonify(user.to_dict()), 200)

    abort(400, description="Invalid file type")
