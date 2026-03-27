#!/usr/bin/python3
""" objects that handle all API actions for sign in """
from models.user import User
from models import storage
from api.v0.views import app_views
from flask import jsonify, request
from flasgger.utils import swag_from
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models.enum import UserType


def users_search(data=""):
    """
    Retrieves a user object with a certain username
    """
    if not data or not len(data): 
        return None

    all_users = storage.all(User).values()
    for users in all_users:
        if users.email == data:
            return users
    return None


@app_views.route('/login', methods=["POST"], strict_slashes=False)
@swag_from('documentation/users/post_signin.yml', methods=['POST'])
def login_user():
    """
    Log in an existing user and return a JWT access token.
    Expects JSON data with 'email' and 'password'.
    """
    data = request.get_json()
    email = data.get("email", None)
    password = data.get("password", None)

    user = users_search(email)

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Create the access token for the logged-in user
    iden = user.id
    access_token = create_access_token(identity=iden)
    return jsonify(access_token=access_token), 200

@app_views.route('/admin/login', methods=["POST"], strict_slashes=False)
@swag_from('documentation/users/post_signin_admin.yml', methods=['POST'])
def login_admin():
    """
    Log in an existing admin and return a JWT access token.
    Expects JSON data with 'email' and 'password'.
    """
    data = request.get_json()
    email = data.get("email", None)
    password = data.get("password", None)

    user = users_search(email)

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401
    if (user.user_type == 'admin'):
        return jsonify({"message": "Invalid email or password"}), 401

    # Create the access token for the logged-in user
    iden = user.id
    access_token = create_access_token(identity=iden)
    return jsonify(access_token=access_token), 200

@app_views.route("/dashboard", methods=["GET"])
@jwt_required()
def user_dashboard():
    """
    A protected route that requires a valid JWT access Token.
    Returns a personalized welcome message for the user
    """
    current_user = get_jwt_identity()
    return jsonify({
        "id": current_user
    }), 200
