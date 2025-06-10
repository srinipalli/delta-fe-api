import pandas as pd
from typing import Dict, Any
import io

def generate_excel(data: Dict[str, Any]) -> io.BytesIO:
    """
    Generate Excel file from test cases
    Args:
        data: Dictionary containing story and test cases data
    Returns:
        BytesIO object containing the Excel file
    """
    # Create a list to store all test case data
    test_case_data = []
    
    # Add story information
    story_info = {
        'Story ID': data['story']['id'],
        'Story Description': data['story']['description']
    }
    
    # Process each test case
    for tc in data['test_cases']:
        test_case_data.append({
            'Test Case ID': tc['test_case_id'],
            'Description': tc['description'],
            'Steps': '\n'.join([f"{i+1}. {step}" for i, step in enumerate(tc['steps'])]),
            'Expected Result': tc['expected_result']
        })
    
    # Create DataFrame
    df = pd.DataFrame(test_case_data)
    
    # Create Excel writer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write story information
        pd.DataFrame([story_info]).to_excel(writer, sheet_name='Test Cases', index=False, startrow=0)
        
        # Write test cases
        df.to_excel(writer, sheet_name='Test Cases', index=False, startrow=2)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Test Cases']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
    
    # Reset buffer position
    output.seek(0)
    return output 