import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create PostgreSQL database and tables"""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Create database if it doesn't exist
    db_name = os.getenv('POSTGRES_DB')
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f'CREATE DATABASE {db_name}')
    
    cur.close()
    conn.close()
    
    # Connect to the new database and create tables
    conn = psycopg2.connect(
        dbname=db_name,
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    cur = conn.cursor()
    
    # Create user_stories table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_stories (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create test_cases_generated table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_cases_generated (
            id SERIAL PRIMARY KEY,
            story_id INTEGER REFERENCES user_stories(id),
            test_cases JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("Database and tables created successfully!")

if __name__ == "__main__":
    create_database() 