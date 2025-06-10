import psycopg2
import lancedb
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class DatabaseService:
    def __init__(self, postgres_config: Dict[str, Any], lance_db_path: str):
        """Initialize database connections"""
        self.postgres_config = postgres_config
        self.lance_db_path = lance_db_path
        self.lance_db = lancedb.connect(lance_db_path)
   
    def get_recent_stories(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get paginated stories with test case information from both PostgreSQL and LanceDB
        
        Args:
            page: Page number (starts from 1)
            per_page: Number of items per page
            
        Returns:
            Dictionary containing:
            - stories: List of stories for the current page
            - total: Total number of stories
            - total_pages: Total number of pages
            - current_page: Current page number
            - per_page: Number of items per page
        """
        try:
            # Get stories from LanceDB
            stories_table = self.lance_db.open_table("user_stories")
            lance_stories = stories_table.to_pandas()
            
            # Sort stories by timestamp in descending order (latest first)
            lance_stories = lance_stories.sort_values(by='time_stamp', ascending=False)
            
            # Calculate pagination
            total_stories = len(lance_stories)
            total_pages = (total_stories + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            # Get paginated stories
            paginated_stories = lance_stories.iloc[start_idx:end_idx]
            
            stories = []
            for _, lance_story in paginated_stories.iterrows():
                story_id = int(lance_story['story_id'])
                
                # Get test case count from PostgreSQL
                with psycopg2.connect(**self.postgres_config) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT num_test_cases, end_time
                            FROM test_cases_generated
                            WHERE story_id = %s
                        """, (story_id,))
                        pg_result = cur.fetchone()
                
                stories.append({
                    'id': story_id,
                    'description': lance_story['story_Description'],
                    'num_test_cases': pg_result[0] if pg_result else 0,
                    'download_link': f'/api/testcases/download/{story_id}',
                    'process_start_time': lance_story['time_stamp'].isoformat(),
                    'process_end_time': pg_result[1].isoformat() if pg_result and pg_result[1] else None
                })
            
            return {
                'stories': stories,
                'total': total_stories,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            print(f"Error getting recent stories: {str(e)}")
            return {
                'stories': [],
                'total': 0,
                'total_pages': 0,
                'current_page': page,
                'per_page': per_page
            }
        
    def get_story(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific story by ID from both LanceDB and PostgreSQL"""
        try:
            # Get story from LanceDB
            stories_table = self.lance_db.open_table("user_stories")
            story_data = stories_table.to_pandas()
            lance_story = story_data[story_data['story_id'] == story_id]
            
            if lance_story.empty:
                return None
            
            # Get test case information from PostgreSQL
            with psycopg2.connect(**self.postgres_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT num_test_cases, end_time
                        FROM test_cases_generated
                        WHERE story_id = %s
                    """, (story_id,))
                    pg_result = cur.fetchone()
            
            return {
                'id': story_id,
                'description': lance_story['story_Description'].iloc[0],
                'num_test_cases': pg_result[0] if pg_result else 0,
                'download_link': f'/api/testcases/download/{story_id}',
                'process_start_time': lance_story['time_stamp'].iloc[0].isoformat(),
                'process_end_time': pg_result[1].isoformat() if pg_result and pg_result[1] else None
            }
        except Exception as e:
            print(f"Error getting story {story_id}: {str(e)}")
            return None
        
