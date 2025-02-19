import pandas as pd
import json

def analyze_excel(file_path):
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Dictionary to store analysis results
    analysis_results = []
    
    # Loop through sheets and process each course
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Ensure necessary columns exist
        required_columns = ['Total', 'Distinction', 'First Class', 'Second Class', 'Fail', 'ATKT', 'Pass']
        if not all(col in df.columns for col in required_columns):
            continue
        
        total_students = df['Total'].sum()
        distinction = df['Distinction'].sum()
        first_class = df['First Class'].sum()
        second_class = df['Second Class'].sum()
        fail = df['Fail'].sum()
        atkt = df['ATKT'].sum()
        pass_count = df['Pass'].sum()
        
        # Compute percentages
        distinction_pct = (distinction / total_students) * 100
        first_class_pct = (first_class / total_students) * 100
        second_class_pct = (second_class / total_students) * 100
        fail_pct = (fail / total_students) * 100
        atkt_pct = (atkt / total_students) * 100
        pass_pct = (pass_count / total_students) * 100
        
        # Store the results
        analysis_results.append({
            'Class': sheet_name,
            'Total': total_students,
            'Distinction': distinction,
            'Distinction %': round(distinction_pct, 2),
            'First Class': first_class,
            'First Class %': round(first_class_pct, 2),
            'Second Class': second_class,
            'Second Class %': round(second_class_pct, 2),
            'Fail': fail,
            'Fail %': round(fail_pct, 2),
            'ATKT': atkt,
            'ATKT %': round(atkt_pct, 2),
            'Pass': pass_count,
            'Pass %': round(pass_pct, 2)
        })
    
    # Convert results into JSON
    result_json = json.dumps(analysis_results, indent=4)
    
    # Save JSON file
    output_file = file_path.replace('.xlsx', '_analysis.json')
    with open(output_file, 'w') as f:
        f.write(result_json)
    
    print(f"Analysis completed. Results saved to {output_file}")
    return result_json

# Example usage:
analyze_excel('output15.xlsx')
