from flask import Blueprint, jsonify, request
from app.services.db_service import DatabaseService
from flask import current_app

stories_bp = Blueprint('stories', __name__)

@stories_bp.route('/', methods=['GET'])
def get_recent_stories():
    """Get recent stories"""
    try:
        db_service = current_app.config['DB_SERVICE']
        stories = db_service.get_recent_stories()
        return jsonify(stories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stories_bp.route('/<int:story_id>', methods=['GET'])
def get_story(story_id):
    """Get a specific story by ID"""
    try:
        db_service = current_app.config['DB_SERVICE']
        story = db_service.get_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        return jsonify(story)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 