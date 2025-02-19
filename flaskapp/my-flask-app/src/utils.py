import pdfplumber
import pandas as pd
import re
import json
import os
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

def process_pdf_file(filepath):
    """Process PDF file and return analysis results."""
    try:
        data = extract_data_from_pdf(filepath)
        df = pd.DataFrame(data)
        
        # Calculate percentage for all students
        df['Total Marks'] = pd.to_numeric(df['Total Marks'])
        df['Percentage'] = (df['Total Marks'] / 1000) * 100
        
        # Get analysis results
        toppers_data = analyze_toppers(df)
        analysis_data = analyze_results(df)
        
        # Create Excel files
        excel_files = create_excel_files(data, toppers_data, analysis_data)
        
        return {
            'toppers': toppers_data,
            'analysis': analysis_data,
            'excel_files': excel_files
        }
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

def extract_data_from_pdf(pdf_path):
    """Extract data from PDF using pdfplumber."""
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        current_semester = "Unknown"
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if text:
                semester_match = re.search(r'RESULT SHEET FOR THE (.+? SEMESTER \(\w+\))', text, re.IGNORECASE)
                if semester_match:
                    current_semester = semester_match.group(1).strip()
                data.extend(parse_text(text, current_semester))
    return data

def parse_text(text, semester):
    """Parse extracted text from PDF."""
    records = []
    university = "Maharashtra State Board of Technical Education, Mumbai"
    institute = re.search(r'INSTITUTE : (.+?) COURSE', text)
    course = re.search(r'COURSE : (.+?)\n', text)
    
    institute = institute.group(1).strip() if institute else "Unknown"
    course = course.group(1).strip() if course else "Unknown"
    
    # Use appropriate pattern based on semester type
    if "(K)" in semester:
        student_pattern = re.compile(
            r'(?P<seat_no>\d{6})\s+'
            r'(?P<enroll_no>\d{10})\s+'
            r'(?P<name>[A-Za-z ]{5,})\s*'
            r'(?P<app_code>[A-Z ]{2,15})?\s*'
            r'Total\s*:\s*(?P<total_marks>\d+)',
            re.DOTALL
        )
    else:
        student_pattern = re.compile(
            r'(?P<seat_no>\d{6})\s+(?P<enroll_no>\d{10})\s+'
            r'(?P<name>(?:[A-Z]+(?:\s+[A-Z]+)*))\s+'
            r'(?P<app_code>[A-Z]+(?:\s+[A-Z0-9]+)*)?\s+'
            r'.*?Total\s*:\s*(?P<total_marks>\d+)',
            re.DOTALL
        )
    
    for match in student_pattern.finditer(text):
        seat_no = match.group("seat_no")
        enroll_no = match.group("enroll_no")
        name = match.group("name").strip()
        total_marks = match.group("total_marks")
        
        result_status_match = re.search(rf'{seat_no}.*?Result\s*:\s*([A-Z .]+)', text, re.DOTALL)
        result_status = result_status_match.group(1).strip() if result_status_match else "UNKNOWN"
        
        record = {
            "Course Name": course,
            "Semester": semester,
            "Student Name": name,
            "Enrollment Number": int(enroll_no),
            "Total Marks": int(total_marks),
            "Result Status": result_status
        }
        records.append(record)
    
    return records

def analyze_toppers(df):
    """Identify toppers from the processed data."""
    # Extract semester numbers
    df["Semester Number"] = df["Semester"].apply(lambda x: {
        "FIRST": 1, "SECOND": 2, "THIRD": 3,
        "FOURTH": 4, "FIFTH": 5, "SIXTH": 6
    }.get(next((k for k in ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH"] 
                if k in x.upper()), None), None))
    
    # Determine year based on semester
    df["Year"] = df["Semester Number"].apply(
        lambda x: "First Year" if x in [1, 2] else 
                 ("Second Year" if x in [3, 4] else "Third Year"))
    
    # Get top 3 students per course and year
    toppers = df.sort_values(["Course Name", "Year", "Total Marks"], 
                           ascending=[True, True, False])
    toppers = toppers.groupby(["Course Name", "Year"]).head(3)
    
    return toppers[["Course Name", "Student Name", "Year", "Total Marks", "Percentage"]].to_dict('records')

def analyze_results(df):
    """Analyze results by course and semester."""
    result_analysis = {}
    for (course, semester), group in df.groupby(["Course Name", "Semester"]):
        total_students = len(group)
        passed = len(group[~group["Result Status"].str.contains("F.T.", na=False)])
        
        # Count different result categories
        distinction = len(group[group["Result Status"].str.contains("DIST.", na=False)])
        first_class = len(group[group["Result Status"].str.contains("FIRST CLASS", na=False)])
        second_class = len(group[group["Result Status"].str.contains("SECOND CLASS", na=False)])
        pass_class = len(group[group["Result Status"].str.contains("PASS CLASS", na=False)])
        atkt = len(group[group["Result Status"].str.contains("ATKT", na=False)])
        fail = len(group[group["Result Status"].str.contains("FAIL|F.T.", na=False, regex=True)])
        
        # Calculate totals
        passed = distinction + first_class + second_class + pass_class
        
        result_analysis.setdefault(course, {})[semester] = {
            "Total Students": total_students,
            "Pass": passed,
            "Pass Percentage": round((passed / total_students) * 100, 2),
            "Distinction": distinction,
            "First Class": first_class,
            "Second Class": second_class,
            "Pass Class": pass_class,
            "ATKT": atkt,
            "Fail": fail,
            "Grade Distribution": {
                "Distinction": round((distinction / total_students) * 100, 2),
                "First Class": round((first_class / total_students) * 100, 2),
                "Second Class": round((second_class / total_students) * 100, 2),
                "Pass Class": round((pass_class / total_students) * 100, 2),
                "ATKT": round((atkt / total_students) * 100, 2),
                "Fail": round((fail / total_students) * 100, 2)
            }
        }
    
    return result_analysis

def create_excel_files(raw_data, toppers_data, analysis_data):
    """Create three different Excel files for download."""
    excel_files = {}
    
    # 1. Raw Data Excel
    raw_excel = BytesIO()
    df_raw = pd.DataFrame(raw_data)
    df_raw.to_excel(raw_excel, index=False, sheet_name='Extracted Data')
    raw_excel.seek(0)
    excel_files['raw_data'] = raw_excel

    # 2. Toppers Excel
    toppers_excel = BytesIO()
    df_toppers = pd.DataFrame(toppers_data)
    with pd.ExcelWriter(toppers_excel, engine='openpyxl') as writer:
        df_toppers.to_excel(writer, sheet_name='Toppers', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Toppers']
        
        # Style the toppers sheet
        header_fill = PatternFill(start_color='1E88E5', end_color='1E88E5', fill_type='solid')
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = Font(color='FFFFFF', bold=True)
    
    toppers_excel.seek(0)
    excel_files['toppers'] = toppers_excel

    # 3. Analysis Excel
    analysis_excel = BytesIO()
    with pd.ExcelWriter(analysis_excel, engine='openpyxl') as writer:
        # Overall Analysis Sheet
        analysis_rows = []
        for course, semesters in analysis_data.items():
            for semester, stats in semesters.items():
                row = {
                    'Course': course,
                    'Semester': semester,
                    'Total Students': stats['Total Students'],
                    'Pass': stats['Pass'],
                    'Pass Percentage': stats['Pass Percentage'],
                    'Distinction': stats['Distinction'],
                    'First Class': stats['First Class'],
                    'Second Class': stats['Second Class'],
                    'Pass Class': stats['Pass Class'],
                    'ATKT': stats['ATKT'],
                    'Fail': stats['Fail']
                }
                analysis_rows.append(row)
        
        df_analysis = pd.DataFrame(analysis_rows)
        df_analysis.to_excel(writer, sheet_name='Analysis', index=False)

        # Grade Distribution Sheet
        dist_rows = []
        for course, semesters in analysis_data.items():
            for semester, stats in semesters.items():
                row = {
                    'Course': course,
                    'Semester': semester,
                    **stats['Grade Distribution']
                }
                dist_rows.append(row)
        
        df_dist = pd.DataFrame(dist_rows)
        df_dist.to_excel(writer, sheet_name='Grade Distribution', index=False)
    
    analysis_excel.seek(0)
    excel_files['analysis'] = excel_files

    return excel_files