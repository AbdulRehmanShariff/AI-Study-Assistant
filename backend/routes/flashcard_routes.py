from flask import Blueprint
from controllers.flashcard_controller import FlashcardController

flashcard_bp = Blueprint('flashcards', __name__)

@flashcard_bp.route('/generate', methods=['POST'])
def generate():
    return FlashcardController.generate()

@flashcard_bp.route('/<document_id>', methods=['GET'])
def get_by_document(document_id):
    return FlashcardController.get_by_document(document_id)
