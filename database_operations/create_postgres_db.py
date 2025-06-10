import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    conn = psycopg2.connect(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
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
    
    # Create test_cases_generated table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_cases_generated (
            id SERIAL PRIMARY KEY,
            story_id INTEGER NOT NULL,
            test_cases JSONB NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            num_test_cases INTEGER GENERATED ALWAYS AS (jsonb_array_length(test_cases)) STORED
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("Database and tables created successfully!")

if __name__ == "__main__":
    create_database() 