import pdfplumber
import pandas as pd
import re

# Function to extract data from PDF
def extract_data_from_pdf(pdf_path, output_excel):
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        current_semester = "Unknown"
        
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if text:
                semester_match = re.search(r'RESULT SHEET FOR THE (.*?) SEMESTER', text, re.IGNORECASE)
                if semester_match:
                    current_semester = semester_match.group(1).strip()
                
                data.extend(parse_text(text, current_semester))
    
    df = pd.DataFrame(data, columns=["Student ID", "Student Name", "Semester", "Course", "Total Obtained", "Total Marks", "Result"])
    
    # Convert numerical columns to integer type
    df["Student ID"] = pd.to_numeric(df["Student ID"], errors='coerce')
    df["Total Obtained"] = pd.to_numeric(df["Total Obtained"], errors='coerce')
    df["Total Marks"] = pd.to_numeric(df["Total Marks"], errors='coerce')
    
    df.to_excel(output_excel, index=False)
    print(f"Data successfully written to {output_excel}")

# Function to parse extracted text
def parse_text(text, semester):
    records = []
    
    # Extract general information
    course = re.search(r'COURSE : (.+?)\n', text)
    course = course.group(1).strip() if course else "Unknown"
    
    total_match = re.search(r'Total Marks : (\d+)', text)
    total_marks = int(total_match.group(1)) if total_match else None
    
    # Updated regex to capture names more accurately
    student_pattern = re.compile(r'(?P<seat_no>\d{6})\s+(?P<enroll_no>\d{10})\s+(?P<name>[A-Z ]{5,})\s+X Y [SW]\d{2}\s+\d{6}\s+.*?Total : (?P<total_obtained>\d+)', re.DOTALL)
    
    for match in student_pattern.finditer(text):
        seat_no = match.group("seat_no")
        name = match.group("name").strip()
        total_obtained = match.group("total_obtained")
        
        # Extract result status
        result_status_match = re.search(rf'{seat_no}.*?Result : ([A-Z.]+)', text, re.DOTALL)
        result_status = result_status_match.group(1) if result_status_match else "Not Available"
        
        record = {
            "Student ID": int(seat_no),
            "Student Name": name,
            "Semester": semester,
            "Course": course,
            "Total Obtained": int(total_obtained),
            "Total Marks": total_marks,
            "Result": result_status,
        }
        
        records.append(record)
        
        # Stop after collecting 3 students
        if len(records) >= 3:
            break
    
    return records

# Example Usage
pdf_path = "results.pdf"  # Replace with your PDF file
output_excel = "output.xlsx"
extract_data_from_pdf(pdf_path, output_excel)
