from flask import jsonify


def success_response(message, data=None, status=200):
    """Create a standardized success response.

    Args:
        message: Human-readable success message.
        data: Optional response data (dict, list, etc.).
        status: HTTP status code (default 200).

    Returns:
        Flask JSON response tuple.
    """
    response = {
        'success': True,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def error_response(message, error=None, status=400):
    """Create a standardized error response.

    Args:
        message: Human-readable error message.
        error: Optional detailed error code or description.
        status: HTTP status code (default 400).

    Returns:
        Flask JSON response tuple.
    """
    response = {
        'success': False,
        'message': message,
    }
    if error is not None:
        response['error'] = error
    return jsonify(response), status
