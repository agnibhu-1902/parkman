from flask_login import current_user, login_required
from flask import Blueprint, jsonify, send_from_directory
from tasks import export_parking_history_csv

exports_bp = Blueprint('exports', __name__, url_prefix='/api/exports')

@exports_bp.route('/csv', methods=['POST'])
@login_required
def trigger_export():
    try:
        export_parking_history_csv.delay(current_user.id)
        return jsonify(success = True, message = 'Export job started! You\'ll receive an email when it\'s ready.'), 201
    except Exception as e:
        return jsonify(success = False, message = 'Failed to start export job', error = str(e)), 500

@exports_bp.route('/download/<filename>', methods=['GET'])
@login_required
def download_file(filename):
    return send_from_directory('exports', filename, as_attachment=True)