# Database Operations

This directory contains scripts for setting up and managing the databases used in the Test Case Generator project.

## Files

1. `create_postgres_db.py`
   - Creates PostgreSQL database and tables
   - Sets up user_stories and test_cases_generated tables
   - Run with: `python create_postgres_db.py`

2. `create_lance_db.py`
   - Creates LanceDB database and table
   - Sets up user_stories table with vector storage
   - Run with: `python create_lance_db.py`

3. `db_operations.py`
   - Contains DatabaseOperations class for common operations
   - Handles both PostgreSQL and LanceDB operations
   - Example usage included in the file

## Setup Instructions

1. Ensure PostgreSQL is installed and running
2. Create a `.env` file in the project root with database credentials
3. Run the database creation scripts:
   ```bash
   python create_postgres_db.py
   python create_lance_db.py
   ```

## Database Schema

### PostgreSQL Tables

1. `user_stories`
   ```sql
   CREATE TABLE user_stories (
       id SERIAL PRIMARY KEY,
       title VARCHAR(255) NOT NULL,
       description TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. `test_cases_generated`
   ```sql
   CREATE TABLE test_cases_generated (
       id SERIAL PRIMARY KEY,
       story_id INTEGER REFERENCES user_stories(id),
       test_cases JSONB NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### LanceDB Table

`user_stories`
```python
{
    "story_id": "string",
    "vector": "float32[768]",
    "filename": "string",
    "test_case_generated": "boolean",
    "time_stamp": "timestamp"
}
```

## Common Operations

1. Adding a User Story:
   ```python
   db = DatabaseOperations()
   story_id = db.add_user_story(
       title="Story Title",
       description="Story Description",
       vector=[...],  # 768-dimensional vector
       filename="story.txt"
   )
   ```

2. Adding Test Cases:
   ```python
   db.add_test_cases(story_id, {
       "test_cases": [...]
   })
   ```

3. Getting a Story:
   ```python
   story = db.get_story(story_id)
   ```

4. Getting Recent Stories:
   ```python
   stories = db.get_recent_stories(limit=10)
   ```

## Notes

- Always close database connections when done:
  ```python
  db.close()
  ```
- The LanceDB path should be specified in the `.env` file
- PostgreSQL credentials should be properly secured
- Vector dimensions should match the embedding model (768 for Gemini) 