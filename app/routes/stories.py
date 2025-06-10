from flask import Blueprint, jsonify, request, current_app
from app.services.db_service import DatabaseService

stories_bp = Blueprint('stories', __name__)

@stories_bp.route('/', methods=['GET'])
def get_stories():
    """Get paginated stories"""
    try:
        # Get pagination parameters from query string
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:  # Limit maximum items per page
            per_page = 10
            
        db_service = current_app.config['DB_SERVICE']
        result = db_service.get_recent_stories(page=page, per_page=per_page)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stories_bp.route('/<int:story_id>', methods=['GET'])
def get_story(story_id):
    """Get a specific story"""
    try:
        db_service = current_app.config['DB_SERVICE']
        story = db_service.get_story(story_id)
        if story:
            return jsonify(story)
        return jsonify({'error': 'Story not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500 