from flask import Blueprint, request
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    return AuthController.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    return AuthController.login()

@auth_bp.route('/me', methods=['GET'])
def get_me():
    return AuthController.get_me()

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    return AuthController.update_profile()

@auth_bp.route('/password', methods=['PUT'])
def change_password():
    return AuthController.change_password()

@auth_bp.route('/account', methods=['DELETE'])
def delete_account():
    return AuthController.delete_account()
