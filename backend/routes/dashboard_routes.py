from flask import Blueprint, request
from controllers.dashboard_controller import DashboardController

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    return DashboardController.get_stats(request)

