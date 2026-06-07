from flask import Blueprint
from controllers.quiz_controller import QuizController

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/generate', methods=['POST'])
def generate():
    return QuizController.generate()

@quiz_bp.route('/<document_id>', methods=['GET'])
def get_by_document(document_id):
    return QuizController.get_by_document(document_id)
