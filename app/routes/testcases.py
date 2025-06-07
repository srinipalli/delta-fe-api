from flask import Blueprint, jsonify, request, send_file
from app.services.db_service import DatabaseService
from app.utils.excel_util import generate_excel
from flask import current_app

testcases_bp = Blueprint('testcases', __name__)

@testcases_bp.route('/<int:story_id>', methods=['GET'])
def get_test_cases(story_id):
    """Get test cases for a story"""
    try:
        db_service = current_app.config['DB_SERVICE']
        test_cases = db_service.get_test_cases(story_id)
        return jsonify(test_cases)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@testcases_bp.route('/<int:story_id>/download', methods=['GET'])
def download_test_cases(story_id):
    """Download test cases as Excel file"""
    try:
        db_service = current_app.config['DB_SERVICE']
        test_cases = db_service.get_test_cases(story_id)
        
        # Generate Excel file
        excel_file = generate_excel(test_cases)
        
        # Send file
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'test_cases_story_{story_id}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500 