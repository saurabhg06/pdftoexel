import pdfplumber
import pandas as pd
import re

def extract_data_from_pdf(pdf_path, output_excel):
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                data.extend(parse_text(text))
    
    df = pd.DataFrame(data)
    df.to_excel(output_excel, index=False)
    print(f"Data successfully written to {output_excel}")

def parse_text(text):
    records = []
    
    # Extract general information
    university = "Maharashtra State Board of Technical Education, Mumbai"
    institute = re.search(r'INSTITUTE : (.+?) COURSE', text).group(1).strip()
    course = re.search(r'COURSE : (.+?)\n', text).group(1).strip()
    exam_session = re.search(r'EXAMINATION HELD IN (.+?) \(', text).group(1).strip()
    result_date = re.search(r'Result Date : (\d{2}/\d{2}/\d{4})', text).group(1)
    
    # Extract student results
    student_pattern = re.compile(r'(\d{6})\s+(\d{10})\s+([A-Z ]+)\s+X Y [SW]\d{2}\s+\d{6}\s+(.+?)Total : (\d+)', re.DOTALL)
    
    for match in student_pattern.finditer(text):
        seat_no, enroll_no, name, marks_section, total_marks = match.groups()
        marks = re.findall(r'(\d{2,3})[#*]', marks_section)
        
        result_status_match = re.search(r'Result : ([A-Z.]+)', marks_section)
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
        
        subjects = ["ENG", "ENG PR", "BSC", "BSC PR", "BMS", "ICT", "EGM", "WPM"]
        subject_marks = marks[:24]  # Extract first 24 marks
        
        for i, subject in enumerate(subjects):
            record[f"{subject} (ESE)"] = subject_marks[i * 3] if i * 3 < len(subject_marks) else ""
            record[f"{subject} (ISE)"] = subject_marks[i * 3 + 1] if i * 3 + 1 < len(subject_marks) else ""
            record[f"{subject} (Total)"] = subject_marks[i * 3 + 2] if i * 3 + 2 < len(subject_marks) else ""
        
        records.append(record)
    
    return records

# Example Usage
pdf_path = "results.pdf"  # Replace with your PDF file
output_excel = "output.xlsx"
extract_data_from_pdf(pdf_path, output_excel)