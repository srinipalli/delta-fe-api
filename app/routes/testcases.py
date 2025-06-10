from flask import Blueprint, jsonify, request, send_file
from app.services.db_service import DatabaseService
from app.utils.excel_util import generate_excel
from flask import current_app
import json
import psycopg2

testcases_bp = Blueprint('testcases', __name__)


@testcases_bp.route('/download/<int:story_id>', methods=['GET'])
def download_test_cases(story_id):
    """Download test cases as Excel file"""
    try:
        db_service = current_app.config['DB_SERVICE']
        
        # Get story details from LanceDB
        stories_table = db_service.lance_db.open_table("user_stories")
        story_data = stories_table.to_pandas()
        lance_story = story_data[story_data['story_id'] == story_id]
        
        if lance_story.empty:
            return jsonify({'error': 'Story not found'}), 404
        
        # Get test cases from PostgreSQL
        with psycopg2.connect(**db_service.postgres_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT test_cases
                    FROM test_cases_generated
                    WHERE story_id = %s
                """, (story_id,))
                test_cases_row = cur.fetchone()
                
                if not test_cases_row:
                    return jsonify({'error': 'No test cases found'}), 404
                
                test_cases = test_cases_row[0]
        
        # Prepare data for Excel generation
        excel_data = {
            'story': {
                'id': story_id,
                'description': lance_story['story_Description'].iloc[0]
            },
            'test_cases': test_cases
        }
        
        # Generate Excel file
        excel_file = generate_excel(excel_data)
        
        # Send file
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'test_cases_story_{story_id}.xlsx'
        )
    except Exception as e:
        print(f"Error downloading test cases: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500 