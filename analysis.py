import pandas as pd
import json

# Function to analyze the result data and generate JSON output
def analyze_results(input_excel, output_json):
    # Read the Excel file
    df = pd.read_excel(input_excel)
    
    # Group by course and semester
    grouped_data = df.groupby(["Course", "Semester"])
    
    analysis_results = {}
    
    for (course, semester), group in grouped_data:
        total_students = len(group)
        passed_students = len(group[group["Result"] == "PASS"])
        failed_students = len(group[group["Result"] == "FAIL"])
        distinction = len(group[group["Total Obtained"] >= 75])
        first_class = len(group[(group["Total Obtained"] >= 60) & (group["Total Obtained"] < 75)])
        second_class = len(group[(group["Total Obtained"] >= 50) & (group["Total Obtained"] < 60)])
        pass_percentage = (passed_students / total_students) * 100 if total_students > 0 else 0
        
        analysis_results.setdefault(course, {})[semester] = {
            "Total Students": total_students,
            "Passed Students": passed_students,
            "Failed Students": failed_students,
            "Distinction": distinction,
            "First Class": first_class,
            "Second Class": second_class,
            "Pass Percentage": round(pass_percentage, 2)
        }
    
    # Save results in JSON format
    with open(output_json, "w") as json_file:
        json.dump(analysis_results, json_file, indent=4)
    
    print(f"Analysis JSON successfully saved to {output_json}")

# Example Usage
input_excel = "output.xlsx"  # Replace with your Excel file
output_json = "analysis_results.json"
analyze_results(input_excel, output_json)
