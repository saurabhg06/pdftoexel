import pdfplumber
import pandas as pd
import re

# Function to extract data from PDF
def extract_data_from_pdf(pdf_path, output_excel):
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                data.extend(parse_text(text))
    
    df = pd.DataFrame(data, columns=["University Name", "Institute Name", "Course Name", "Semester", "Exam Session", "Result Date", "Student Name", "Enrollment Number", "Seat Number", "Total Marks", "Total", "Result Status"])
    df.to_excel(output_excel, index=False)
    print(f"Data successfully written to {output_excel}")

# Function to parse extracted text
def parse_text(text):
    records = []
    
    # Extract general information
    university = "Maharashtra State Board of Technical Education, Mumbai"
    institute = re.search(r'INSTITUTE : (.+?) COURSE', text).group(1).strip()
    course = re.search(r'COURSE : (.+?)\n', text).group(1).strip()
    semester = re.search(r'RESULT SHEET FOR THE (.*?) SEMESTER', text, re.IGNORECASE).group(1).strip()
    exam_session = re.search(r'EXAMINATION HELD IN (.+?) \(', text).group(1).strip()
    result_date_match = re.search(r'Result Date : (\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    result_date = result_date_match.group(1) if result_date_match else "Unknown"
    total_match = re.search(r'Total Marks : (\d+)', text)
    total = total_match.group(1) if total_match else "Unknown"
    
    # Extract student results
    student_pattern = re.compile(r'(\d{6})\s+(\d{10})\s+([A-Z ]+)\s+X Y [SW]\d{2}\s+\d{6}\s+(.+?)Total : (\d+)', re.DOTALL)
    
    for match in student_pattern.finditer(text):
        seat_no, enroll_no, name, _, total_marks = match.groups()
        
        # Extract result status
        result_status_match = re.search(rf'{seat_no}.*?Result : ([A-Z.]+)', text, re.DOTALL)
        result_status = result_status_match.group(1) if result_status_match else "Not Available"
        
        record = {
            "University Name": university,
            "Institute Name": institute,
            "Course Name": course,
            "Semester": semester,
            "Exam Session": exam_session,
            "Result Date": result_date,
            "Student Name": name.strip(),
            "Enrollment Number": enroll_no,
            "Seat Number": seat_no,
            "Total Marks": total_marks,
            "Total": total,
            "Result Status": result_status,
        }
        
        records.append(record)
    
    return records

# Example Usage
pdf_path = "results.pdf"  # Replace with your PDF file
output_excel = "output.xlsx"
extract_data_from_pdf(pdf_path, output_excel)
