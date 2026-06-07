from flask import Blueprint
from controllers.summary_controller import SummaryController

summary_bp = Blueprint('summaries', __name__)

@summary_bp.route('/generate', methods=['POST'])
def generate():
    return SummaryController.generate()
