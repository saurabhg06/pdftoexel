import pdfplumber
import pandas as pd
import re

# Function to extract and parse data from the PDF
def extract_pdf_data(pdf_path):
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                
                # Extract University and Institute details
                university_name = lines[0].strip()
                institute_name = lines[1].split(":")[1].strip()
                course_name = lines[2].split(":")[1].strip()
                exam_session = "Winter 2023"
                result_date_match = re.search(r'Result Date : (\d{2}/\d{2}/\d{4})', text)
                result_date = result_date_match.group(1) if result_date_match else "Unknown"
                
                # Extract Student Details
                for i in range(6, len(lines)):
                    parts = lines[i].split()
                    if len(parts) > 5 and parts[0].isdigit():  # Ensuring it's a student record
                        seat_number = parts[0]
                        enrollment_number = parts[1]
                        student_name = " ".join(parts[2:-4])
                        result_status = parts[-4]
                        application_code = parts[-3]
                        total_marks = parts[-2]
                        result_remarks = parts[-1]
                        
                        # Extract subject-wise marks
                        ese_marks = list(map(str, re.findall(r'\d+', lines[i + 1])))  # ESE Marks
                        ise_marks = list(map(str, re.findall(r'\d+', lines[i + 2])))  # ISE Marks
                        total_subject_marks = list(map(str, re.findall(r'\d+', lines[i + 3])))  # Total Marks
                        
                        if len(ese_marks) < 8:
                            ese_marks += ["N/A"] * (8 - len(ese_marks))
                        if len(ise_marks) < 8:
                            ise_marks += ["N/A"] * (8 - len(ise_marks))
                        if len(total_subject_marks) < 8:
                            total_subject_marks += ["N/A"] * (8 - len(total_subject_marks))
                        
                        data.append([
                            university_name, institute_name, course_name, exam_session, result_date,
                            student_name, enrollment_number, seat_number, application_code, total_marks, result_status,
                            *ese_marks, *ise_marks, *total_subject_marks
                        ])
    
    return data

# Convert extracted data to Excel
def save_to_excel(data, output_path):
    columns = [
        "University Name", "Institute Name", "Course Name", "Exam Session", "Result Date",
        "Student Name", "Enrollment Number", "Seat Number", "Application Code", "Total Marks", "Result Status",
        "ENG (ESE)", "BSC (ESE)", "BSC PR (ESE)", "BMS (ESE)", "ICT (ESE)", "EGM (ESE)", "WPM (ESE)", "ENG PR (ESE)",
        "ENG (ISE)", "BSC (ISE)", "BSC PR (ISE)", "BMS (ISE)", "ICT (ISE)", "EGM (ISE)", "WPM (ISE)", "ENG PR (ISE)",
        "ENG (Total)", "BSC (Total)", "BSC PR (Total)", "BMS (Total)", "ICT (Total)", "EGM (Total)", "WPM (Total)", "ENG PR (Total)"
    ]
    
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(output_path, index=False)
    print(f"Excel file saved successfully: {output_path}")

# Run the script
pdf_path = "results.pdf"  # Change this to the actual PDF file path
output_excel_path = "output.xlsx"
data = extract_pdf_data(pdf_path)
save_to_excel(data, output_excel_path)
