import pdfplumber 
import pandas as pd
import re

def extract_data_from_pdf(pdf_path, output_excel):
    """
    Extract data from PDF and save to Excel file.
    
    Args:
        pdf_path (str): Path to input PDF file
        output_excel (str): Path for output Excel file
    """
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
    
    # Create DataFrame and process data
    df = create_dataframe(data)
    df.to_excel(output_excel, index=False)
    print(f"Data successfully written to {output_excel}")

def create_dataframe(data):
    """Create and process DataFrame from extracted data."""
    columns = [
        "University Name", "Institute Name", "Course Name", "Semester", 
        "Exam Session", "Result Date", "Student Name", "Enrollment Number", 
        "Seat Number", "Total Marks", "Total", "Percentage", "Result Status"
    ]
    
    df = pd.DataFrame(data, columns=columns)
    
    # Convert numerical columns
    numeric_columns = ["Enrollment Number", "Seat Number", "Total Marks", "Total"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate percentage
    df["Percentage"] = (df["Total Marks"] / df["Total"]) * 100
    df["Percentage"] = df["Percentage"].fillna(0).round(2)
    
    return df

def parse_text(text, semester):
    """Parse extracted text and return list of records."""
    records = []
    
    # Extract general information
    university = "Maharashtra State Board of Technical Education, Mumbai"
    info = extract_general_info(text)
    
    # Select appropriate pattern based on semester
    student_pattern = get_student_pattern(semester)
    
    # Process each student record
    for match in student_pattern.finditer(text):
        record = create_student_record(match, text, university, info, semester)
        records.append(record)
    
    return records

def extract_general_info(text):
    """Extract general information from text."""
    patterns = {
        'institute': (r'INSTITUTE : (.+?) COURSE', "Unknown"),
        'course': (r'COURSE : (.+?)\n', "Unknown"),
        'exam_session': (r'EXAMINATION HELD IN (.+?) \(', "Unknown"),
        'result_date': (r'Result Date : (\d{2}/\d{2}/\d{4})', "Unknown"),
        'total': (r'Total Marks : (\d+)', None)
    }
    
    info = {}
    for key, (pattern, default) in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        value = match.group(1).strip() if match else default
        info[key] = int(value) if key == 'total' and value is not None else value
    
    return info

def get_student_pattern(semester):
    """Return appropriate regex pattern based on semester."""
    if "(K)" in semester:
        return re.compile(
            r'(?P<seat_no>\d{6})\s+'
            r'(?P<enroll_no>\d{10})\s+'
            r'(?P<name>[A-Za-z ]{5,})\s*'
            r'(?P<app_code>[A-Z ]{2,15})?\s*'
            r'Total\s*:\s*(?P<total_marks>\d+)',
            re.DOTALL
        )
    else:
        return re.compile(
            r'(?P<seat_no>\d{6})\s+'
            r'(?P<enroll_no>\d{10})\s+'
            r'(?P<name>(?:[A-Z]+(?:\s+[A-Z]+)*))\s+'
            r'(?P<app_code>[A-Z]+(?:\s+[A-Z0-9]+)*)?\s+'
            r'.*?Total\s*:\s*(?P<total_marks>\d+)',
            re.DOTALL
        )

def create_student_record(match, text, university, info, semester):
    """Create a student record from regex match."""
    seat_no = match.group("seat_no")
    result_status_match = re.search(rf'{seat_no}.*?Result\s*:\s*([A-Z .]+)', text, re.DOTALL)
    result_status = result_status_match.group(1).strip() if result_status_match else "UNKNOWN"
    
    return {
        "University Name": university,
        "Institute Name": info['institute'],
        "Course Name": info['course'],
        "Semester": semester,
        "Exam Session": info['exam_session'],
        "Result Date": info['result_date'],
        "Student Name": match.group("name").strip(),
        "Enrollment Number": int(match.group("enroll_no")),
        "Seat Number": int(seat_no),
        "Total Marks": int(match.group("total_marks")),
        "Total": info['total'],
        "Percentage": (int(match.group("total_marks")) / info['total']) * 100 if info['total'] else 0,
        "Result Status": result_status
    }