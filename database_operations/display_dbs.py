import psycopg2
import lancedb
import pandas as pd
from tabulate import tabulate
import os
from dotenv import load_dotenv
import json

load_dotenv()

def display_databases():
    print("\n=== Displaying Database Contents ===\n")
    
    # Display LanceDB contents
    print("=== LanceDB User Stories ===")
    try:
        lance_db_path = os.getenv('LANCE_DB_PATH', 'data/lance_db')
        lance_db = lancedb.connect(lance_db_path)
        
        if 'user_stories' in lance_db.table_names():
            stories_table = lance_db.open_table("user_stories")
            stories_df = stories_table.to_pandas()
            
            # Format the display
            display_df = stories_df[['story_id', 'story_Description', 'Processed_Flag', 'time_stamp']]
            display_df.columns = ['ID', 'Description', 'Processed', 'Timestamp']
            
            print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
            print(f"\nTotal stories in LanceDB: {len(stories_df)}")
        else:
            print("No user_stories table found in LanceDB")
    except Exception as e:
        print(f"Error accessing LanceDB: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # Display PostgreSQL contents
    print("=== PostgreSQL Test Cases ===")
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        cur = conn.cursor()
        
        # Get test cases summary
        cur.execute("""
            SELECT 
                story_id,
                num_test_cases,
                start_time,
                end_time
            FROM test_cases_generated
            ORDER BY story_id
        """)
        
        test_cases = cur.fetchall()
        
        if test_cases:
            # Format the display
            headers = ['Story ID', 'Number of Test Cases', 'Start Time', 'End Time']
            print(tabulate(test_cases, headers=headers, tablefmt='grid'))
            
            # Display detailed test cases for each story
            for story_id, num_cases, _, _ in test_cases:
                print(f"\nDetailed Test Cases for Story ID {story_id}:")
                cur.execute("""
                    SELECT test_cases
                    FROM test_cases_generated
                    WHERE story_id = %s
                """, (story_id,))
                
                test_cases_data = cur.fetchone()[0]
                for tc in test_cases_data:
                    print(f"\nTest Case ID: {tc['test_case_id']}")
                    print(f"Description: {tc['description']}")
                    print("Steps:")
                    for step in tc['steps']:
                        print(f"  - {step}")
                    print(f"Expected Result: {tc['expected_result']}")
            
            print(f"\nTotal stories with test cases: {len(test_cases)}")
        else:
            print("No test cases found in PostgreSQL")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error accessing PostgreSQL: {str(e)}")

if __name__ == "__main__":
    display_databases() 