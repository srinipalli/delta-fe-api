import psycopg2
import psycopg2.extras
import lancedb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def insert_sample_data():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    cur = conn.cursor()

    # Connect to LanceDB
    lance_db_path = os.getenv('LANCE_DB_PATH', 'data/lance_db')
    lance_db = lancedb.connect(lance_db_path)

    # Sample user stories
    stories = [
        {
            'story_id': 1,
            'story_Description': 'As a user, I want to be able to log in to my account using email and password so that I can access my personal dashboard.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=10)
        },
        {
            'story_id': 2,
            'story_Description': 'As a user, I want to be able to reset my password if I forget it so that I can regain access to my account.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=9)
        },
        {
            'story_id': 3,
            'story_Description': 'As a user, I want to be able to update my profile information so that my account details are always current.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=8)
        },
        {
            'story_id': 4,
            'story_Description': 'As a user, I want to be able to view my order history so that I can track my past purchases.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=7)
        },
        {
            'story_id': 5,
            'story_Description': 'As a user, I want to be able to add items to my shopping cart so that I can purchase multiple items at once.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=6)
        },
        {
            'story_id': 6,
            'story_Description': 'As a user, I want to be able to search for products by category so that I can easily find what I am looking for.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=5)
        },
        {
            'story_id': 7,
            'story_Description': 'As a user, I want to be able to filter search results by price range so that I can find products within my budget.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=4)
        },
        {
            'story_id': 8,
            'story_Description': 'As a user, I want to be able to save products to my wishlist so that I can view them later.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=3)
        },
        {
            'story_id': 9,
            'story_Description': 'As a user, I want to be able to receive email notifications about my order status so that I can track my delivery.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=2)
        },
        {
            'story_id': 10,
            'story_Description': 'As a user, I want to be able to rate and review products after purchase so that I can share my experience with others.',
            'Processed_Flag': True,
            'time_stamp': datetime.now() - timedelta(days=1)
        }
    ]

    # Create LanceDB table with sample data
    df = pd.DataFrame(stories)
    # Add vector embeddings (dummy data for now)
    df['story_Description_vector'] = [np.random.rand(768).tolist() for _ in range(len(stories))]
    
    # Create or overwrite the table
    if 'user_stories' in lance_db.table_names():
        lance_db.drop_table('user_stories')
    lance_db.create_table('user_stories', df)
    print("Sample data inserted into LanceDB successfully!")

    # Sample test cases for story_id 1 (10 test cases)
    test_cases = [
        {
            'story_id': 1,
            'test_cases': [
                {
                    'test_case_id': 'TC1.1',
                    'description': 'Verify successful login with valid email and password',
                    'steps': ['Enter valid email', 'Enter valid password', 'Click login button'],
                    'expected_result': 'User should be logged in and redirected to dashboard'
                },
                {
                    'test_case_id': 'TC1.2',
                    'description': 'Verify error message for invalid email format',
                    'steps': ['Enter invalid email format', 'Enter any password', 'Click login button'],
                    'expected_result': 'Error message should display for invalid email format'
                },
                {
                    'test_case_id': 'TC1.3',
                    'description': 'Verify error message for empty password',
                    'steps': ['Enter valid email', 'Leave password empty', 'Click login button'],
                    'expected_result': 'Error message should display for empty password'
                },
                {
                    'test_case_id': 'TC1.4',
                    'description': 'Verify error message for incorrect password',
                    'steps': ['Enter valid email', 'Enter incorrect password', 'Click login button'],
                    'expected_result': 'Error message should display for incorrect password'
                },
                {
                    'test_case_id': 'TC1.5',
                    'description': 'Verify remember me functionality',
                    'steps': ['Enter valid credentials', 'Check remember me box', 'Click login button', 'Logout', 'Reopen browser'],
                    'expected_result': 'Email should be pre-filled on login page'
                },
                {
                    'test_case_id': 'TC1.6',
                    'description': 'Verify password field masks input',
                    'steps': ['Enter password in password field'],
                    'expected_result': 'Password should be masked with asterisks'
                },
                {
                    'test_case_id': 'TC1.7',
                    'description': 'Verify login button is disabled with empty fields',
                    'steps': ['Leave email empty', 'Leave password empty'],
                    'expected_result': 'Login button should be disabled'
                },
                {
                    'test_case_id': 'TC1.8',
                    'description': 'Verify maximum login attempts',
                    'steps': ['Enter valid email', 'Enter incorrect password', 'Repeat 5 times'],
                    'expected_result': 'Account should be temporarily locked after 5 failed attempts'
                },
                {
                    'test_case_id': 'TC1.9',
                    'description': 'Verify session timeout',
                    'steps': ['Login successfully', 'Leave browser idle for 30 minutes'],
                    'expected_result': 'User should be logged out and redirected to login page'
                },
                {
                    'test_case_id': 'TC1.10',
                    'description': 'Verify concurrent login handling',
                    'steps': ['Login from first browser', 'Attempt login from second browser'],
                    'expected_result': 'First session should be terminated and second login should succeed'
                }
            ],
            'start_time': datetime.now() - timedelta(days=10),
            'end_time': datetime.now() - timedelta(days=10, minutes=5)
        }
    ]

    # Insert test cases into PostgreSQL
    for test_case in test_cases:
        cur.execute("""
            INSERT INTO test_cases_generated (story_id, test_cases, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        """, (
            test_case['story_id'],
            psycopg2.extras.Json(test_case['test_cases']),
            test_case['start_time'],
            test_case['end_time']
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("Sample data inserted into PostgreSQL successfully!")

if __name__ == "__main__":
    insert_sample_data() 