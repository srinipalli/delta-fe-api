import pandas as pd
from typing import Dict, Any
import io

def generate_excel(test_cases: Dict[str, Any]) -> io.BytesIO:
    """
    Generate Excel file from test cases
    Args:
        test_cases: Dictionary containing test cases data
    Returns:
        BytesIO object containing the Excel file
    """
    # Create a list to store all test case data
    test_case_data = []
    
    # Process each test case
    for tc in test_cases['test_cases']:
        # Create a row for each step
        for step in tc['steps']:
            test_case_data.append({
                'Test Case ID': tc['id'],
                'Title': tc['title'],
                'Description': tc['description'],
                'Preconditions': '\n'.join(tc['preconditions']),
                'Step Number': step['step'],
                'Action': step['action'],
                'Expected Result': step['expected_result'],
                'Priority': tc['priority'],
                'Type': tc['type']
            })
    
    # Create DataFrame
    df = pd.DataFrame(test_case_data)
    
    # Create Excel writer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write to Excel
        df.to_excel(writer, sheet_name='Test Cases', index=False)
        
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