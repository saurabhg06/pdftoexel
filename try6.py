import pdfplumber
import pandas as pd
import re
from collections import defaultdict

def extract_data_from_pdf(pdf_path, output_excel):
    course_data = defaultdict(list)
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                course, records = parse_text(text)
                if course:
                    course_data[course].extend(records)
    
    with pd.ExcelWriter(output_excel) as writer:
        for course, records in course_data.items():
            df = pd.DataFrame(records)
            df.to_excel(writer, sheet_name=course[:30], index=False)  # Sheet names limited to 30 chars
    print(f"Data successfully written to {output_excel}")

def parse_text(text):
    records = []
    
    # Extract general information
    university = "Maharashtra State Board of Technical Education, Mumbai"
    institute_match = re.search(r'INSTITUTE : (.+?) COURSE', text)
    course_match = re.search(r'COURSE : (.+?)\n', text)
    exam_session_match = re.search(r'EXAMINATION HELD IN (.+?) \(', text)
    result_date_match = re.search(r'Result Date : (\d{2}/\d{2}/\d{4})', text)
    
    if not (institute_match and course_match and exam_session_match and result_date_match):
        return None, []
    
    institute = institute_match.group(1).strip()
    course = course_match.group(1).strip()
    exam_session = exam_session_match.group(1).strip()
    result_date = result_date_match.group(1)
    
    # Identify subjects dynamically
    subject_headers = re.findall(r'([A-Z]+)\s+(?:TH|PR)', text)
    unique_subjects = list(dict.fromkeys(subject_headers))  # Preserve order and remove duplicates
    
    # Extract student results
    student_pattern = re.compile(r'(\d{6})\s+(\d{10})\s+([A-Z ]+)\s+X Y [SW]\d{2}\s+\d{6}\s+(.+?)Total : (\d+)', re.DOTALL)
    
    for match in student_pattern.finditer(text):
        seat_no, enroll_no, name, marks_section, total_marks = match.groups()
        marks = re.findall(r'(\d{2,3})[#*]', marks_section)
        
        result_status_match = re.search(rf'{seat_no}.*?Result : ([A-Z.]+)', text, re.DOTALL)
        result_status = result_status_match.group(1) if result_status_match else "Not Available"
        
        record = {
            "University Name": university,
            "Institute Name": institute,
            "Course Name": course,
            "Exam Session": exam_session,
            "Result Date": result_date,
            "Student Name": name.strip(),
            "Enrollment Number": enroll_no,
            "Seat Number": seat_no,
            "Application Code": "",
            "Total Marks": total_marks,
            "Result Status": result_status,
        }
        
        # Assign subject marks dynamically
        for i, subject in enumerate(unique_subjects):
            record[f"{subject} (ESE)"] = marks[i * 3] if i * 3 < len(marks) else ""
            record[f"{subject} (ISE)"] = marks[i * 3 + 1] if i * 3 + 1 < len(marks) else ""
            record[f"{subject} (Total)"] = marks[i * 3 + 2] if i * 3 + 2 < len(marks) else ""
        
        records.append(record)
    
    return course, records

# Example Usage
pdf_path = "results.pdf"  # Replace with your PDF file
output_excel = "output.xlsx"
extract_data_from_pdf(pdf_path, output_excel)
