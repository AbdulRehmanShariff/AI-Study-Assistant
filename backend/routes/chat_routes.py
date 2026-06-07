from flask import Blueprint
from controllers.chat_controller import ChatController

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/ask', methods=['POST'])
def ask():
    return ChatController.ask()

@chat_bp.route('/history', methods=['GET'])
def get_history():
    return ChatController.get_history()

@chat_bp.route('/history', methods=['DELETE'])
def clear_history():
    return ChatController.clear_history()

@chat_bp.route('/status', methods=['GET'])
def status():
    return ChatController.status()
