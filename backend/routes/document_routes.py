from flask import Blueprint
from controllers.document_controller import DocumentController

document_bp = Blueprint('documents', __name__)

@document_bp.route('/upload', methods=['POST'])
def upload():
    return DocumentController.upload()

@document_bp.route('/', methods=['GET'])
def list_documents():
    return DocumentController.list_documents()

@document_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    return DocumentController.get_document(document_id)

@document_bp.route('/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    return DocumentController.delete_document(document_id)

@document_bp.route('/<document_id>/status', methods=['GET'])
def get_status(document_id):
    return DocumentController.get_status(document_id)
