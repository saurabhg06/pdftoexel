import pdfplumber 
import pandas as pd
import re

# Function to extract data from PDF
def extract_data_from_pdf(pdf_path, output_excel):
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        current_semester = "Unknown"
        
        for page in pdf.pages:
            print(page)
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            
            if text:
                #semester_match = re.search(r'RESULT SHEET FOR THE (.*?) SEMESTER ', text, re.IGNORECASE)
                semester_match = re.search(r'RESULT SHEET FOR THE (.+? SEMESTER \(\w+\))', text, re.IGNORECASE)

                print(semester_match)
                if semester_match:
                    current_semester = semester_match.group(1).strip()
                    print(current_semester)
                
                data.extend(parse_text(text, current_semester))
    
    df = pd.DataFrame(data, columns=[
        "University Name", "Institute Name", "Course Name", "Semester", 
        "Exam Session", "Result Date", "Student Name", "Enrollment Number", 
        "Seat Number", "Total Marks", "Total", "Percentage", "Result Status"
    ])
    
    # Convert numerical columns to numeric type
    df["Enrollment Number"] = pd.to_numeric(df["Enrollment Number"], errors='coerce')
    df["Seat Number"] = pd.to_numeric(df["Seat Number"], errors='coerce')
    df["Total Marks"] = pd.to_numeric(df["Total Marks"], errors='coerce')
    df["Total"] = pd.to_numeric(df["Total"], errors='coerce')

    # Calculate percentage and handle division by zero
    df["Percentage"] = (df["Total Marks"] / df["Total"]) * 100
    df["Percentage"] = df["Percentage"].fillna(0).round(2)  # Replace NaN with 0 and round to 2 decimals

    df.to_excel(output_excel, index=False)
    print(f"Data successfully written to {output_excel}")

# Function to parse extracted text
def parse_text(text, semester):
    records = []
    
    print(text)
    # Extract general information
    university = "Maharashtra State Board of Technical Education, Mumbai"
    institute = re.search(r'INSTITUTE : (.+?) COURSE', text)
    course = re.search(r'COURSE : (.+?)\n', text)
    exam_session = re.search(r'EXAMINATION HELD IN (.+?) \(', text)
    result_date_match = re.search(r'Result Date : (\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    total_match = re.search(r'Total Marks : (\d+)', text)
    
    institute = institute.group(1).strip() if institute else "Unknown"
    course = course.group(1).strip() if course else "Unknown"
    exam_session = exam_session.group(1).strip() if exam_session else "Unknown"
    result_date = result_date_match.group(1) if result_date_match else "Unknown"
    total = int(total_match.group(1)) if total_match else None  # Total possible marks
    
    # Updated regex to capture names more accurately
    #student_pattern = re.compile(r'(?P<seat_no>\d{6})\s+(?P<enroll_no>\d{10})\s+(?P<name>[A-Z ]{5,})\s+X Y [SW]\d{2}\s+\d{6}\s+.*?Total : (?P<total_marks>\d+)', re.DOTALL)
    #print(student_pattern )
    #new regrex
    #student_pattern = re.compile(
    #r'(?P<seat_no>\d{6})\s+(?P<enroll_no>\d{10})\s+'
    #r'(?P<name>(?:[A-Z]+(?:\s+[A-Z]+)*))\s+'
    #r'(?P<app_code>[A-Z]+(?:\s+[A-Z0-9]+)*)?\s+'
    #r'.*?Total\s*:\s*(?P<total_marks>\d+)',
   # re.DOTALL
    if "(K)" in semester :
        print(f"✅ Using Special Pattern for: {semester} (K) or Last Pages")

        # Special pattern for FIRST SEMESTER (K) & last pages
        student_pattern = re.compile(
        r'(?P<seat_no>\d{6})\s+'                     # Seat Number (6 digits)
        r'(?P<enroll_no>\d{10})\s+'                  # Enrollment Number (10 digits)
        r'(?P<name>[A-Za-z ]{5,})\s*'                # Captures full multi-word names (handles lowercase)
        r'(?P<app_code>[A-Z ]{2,15})?\s*'            # Captures App Code (if present), otherwise None
        r'Total\s*:\s*(?P<total_marks>\d+)',         # Captures "Total Marks" (ensures correct match)
        re.DOTALL                                             # Skips marks section (but keeps flexibility)        
)

    else:
        print(f"✅ Using Regular Pattern for: {semester}")

        # Standard pattern for all other semesters
    student_pattern = re.compile(
    r'(?P<seat_no>\d{6})\s+(?P<enroll_no>\d{10})\s+'
    r'(?P<name>(?:[A-Z]+(?:\s+[A-Z]+)*))\s+'
    r'(?P<app_code>[A-Z]+(?:\s+[A-Z0-9]+)*)?\s+'
    r'.*?Total\s*:\s*(?P<total_marks>\d+)',
    re.DOTALL
)

   #last try or just continue
   







    #student_pattern = re.compile(
   # r'(?P<seat_no>\d{6})\s+(?P<enroll_no>\d{10})\s+([A-Z ]+?)\s+X Y [SW]\d{2}\s+\d{6}\s+.*?Total\s*:\s*(?P<total_marks>\d+)',
  #  re.DOTALL
#)
    

    for match in student_pattern.finditer(text):
        seat_no = match.group("seat_no")
        enroll_no = match.group("enroll_no")
        name = match.group("name").strip()
        total_marks = match.group("total_marks")
        print("hello ")
        # Extract result status
        #result_status_match = re.search(rf'{seat_no}.*?Result : ([A-Z.]+)', text, re.DOTALL)
        #result_status = result_status_match.group(1) if result_status_match else "Not Available"
        result_status_match = re.search(rf'{seat_no}.*?Result\s*:\s*([A-Z .]+)', text, re.DOTALL)
        result_status = result_status_match.group(1).strip() if result_status_match else "UNKNOWN"
        record = {
            "University Name": university,
            "Institute Name": institute,
            "Course Name": course,
            "Semester": semester,
            "Exam Session": exam_session,
            "Result Date": result_date,
            "Student Name": name,
            "Enrollment Number": int(enroll_no),
            "Seat Number": int(seat_no),
            "Total Marks": int(total_marks),
            "Total": total,
            "Percentage": (int(total_marks) / total) * 100 if total else 0,  # Handle division by zero
            "Result Status": result_status,
        }
        
        #print(record)
        records.append(record)
    
    return records

# Example Usage
pdf_path = "results.pdf"  # Replace with your PDF file

output_excel = "output15.xlsx"
extract_data_from_pdf(pdf_path, output_excel)
