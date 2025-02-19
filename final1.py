import pdfplumber
import pandas as pd
import re
from collections import defaultdict

def extract_data_from_pdf(pdf_path, output_excel):
    # Dictionary to hold course-wise data: each key maps to a tuple of (subject_headers, records)
    course_data = defaultdict(lambda: {"subject_headers": None, "records": []})
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                course, subj_headers, records = parse_text(text)
                if course:
                    # If we haven't set subject_headers yet for this course, set them.
                    if course_data[course]["subject_headers"] is None:
                        course_data[course]["subject_headers"] = subj_headers
                    else:
                        # Optionally, you could check for consistency here.
                        pass
                    course_data[course]["records"].extend(records)
    
    # Write separate sheets for each course.
    with pd.ExcelWriter(output_excel) as writer:
        for course, data in course_data.items():
            # Fixed general columns
            general_cols = [
                "University Name", "Institute Name", "Course Name", 
                "Exam Session", "Result Date", "Student Name", 
                "Enrollment Number", "Seat Number", "Application Code", 
                "Total Marks", "Result Status"
            ]
            # Use the dynamic subject columns (in order)
            all_cols = general_cols + data["subject_headers"]
            df = pd.DataFrame(data["records"])
            # Reindex to ensure consistent column order; missing columns will be filled with empty strings.
            df = df.reindex(columns=all_cols, fill_value="")
            # Sheet name limited to 30 characters
            df.to_excel(writer, sheet_name=course[:30], index=False)
    print(f"Data successfully written to {output_excel}")

def parse_text(text):
    records = []
    # Extract general information using regex
    institute_match = re.search(r'INSTITUTE : (.+?) COURSE', text)
    course_match = re.search(r'COURSE : (.+?)\n', text)
    exam_session_match = re.search(r'EXAMINATION HELD IN (.+?) \(', text)
    result_date_match = re.search(r'Result Date : (\d{2}/\d{2}/\d{4})', text)
    
    if not (institute_match and course_match and exam_session_match and result_date_match):
        return None, [], []
    
    institute = institute_match.group(1).strip()
    course = course_match.group(1).strip()
    exam_session = exam_session_match.group(1).strip()
    result_date = result_date_match.group(1)
    
    # --- Extract the header section for subject info ---
    # We assume that the header is between "COURSE :" and "SEAT NO."
    try:
        header_section = text.split("COURSE :")[1].split("SEAT NO.")[0].strip()
    except IndexError:
        header_section = ""
    
    # Remove the course name from the header section if present
    header_section = header_section.replace(course, "").strip()
    # Tokenize the header section
    tokens = header_section.split()
    # We expect the tokens in order:
    # [<subject numbers (8 tokens)>, <subject tokens (8 tokens)>, <exam codes (8 tokens)>, then marks header tokens...]
    if len(tokens) < 16:
        subject_tokens = []
    else:
        subject_tokens = tokens[8:16]
    
    # Build subject groups dynamically.
    subject_groups = []
    i = 0
    while i < len(subject_tokens):
        # If two consecutive tokens are identical, treat them as a pair: first remains, second gets " PR"
        if i < len(subject_tokens) - 1 and subject_tokens[i] == subject_tokens[i+1]:
            subject_groups.append(subject_tokens[i])
            subject_groups.append(subject_tokens[i] + " PR")
            i += 2
        else:
            subject_groups.append(subject_tokens[i])
            i += 1
    # Create subject header columns: for each subject group, we expect three columns (ESE, ISE, Total)
    subject_headers = []
    for subj in subject_groups:
        subject_headers.extend([f"{subj} (ESE)", f"{subj} (ISE)", f"{subj} (Total)"])
    
    # --- Extract student rows ---
    # The student row format (based on sample) is assumed as:
    # SEAT_NO (6 digits)  ENROLL_NO (10 digits)  NAME (all caps, may include spaces) 
    # then a fixed pattern "X Y [SW]<2digits>" then another 6-digit number,
    # then a marks section ending with "Total : <total_marks>" and then "Result : <result_status>"
    student_pattern = re.compile(
        r'(\d{6})\s+'
        r'(\d{10})\s+'
        r'([A-Z ]+?)\s+'
        r'X Y [SW]\d{2}\s+\d{6}\s+'
        r'(.+?)Total :\s*(\d+)(?:\s+Result :\s*(\S+))?',
        re.DOTALL
    )
    
    for match in student_pattern.finditer(text):
        seat_no, enroll_no, name, marks_section, total_marks, result_status = match.groups()
        marks = re.findall(r'(\d{2,3})[#*]', marks_section)
        if not result_status:
            result_status = "Not Available"
        
        record = {
            "University Name": "Maharashtra State Board of Technical Education, Mumbai",
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
        
        # There should be 3 marks per subject group.
        for idx, subj in enumerate(subject_groups):
            base = idx * 3
            record[f"{subj} (ESE)"] = marks[base] if base < len(marks) else ""
            record[f"{subj} (ISE)"] = marks[base+1] if base+1 < len(marks) else ""
            record[f"{subj} (Total)"] = marks[base+2] if base+2 < len(marks) else ""
        
        records.append(record)
    
    return course, subject_headers, records

# Example Usage
pdf_path = "results.pdf"   # Replace with the path to your PDF file
output_excel = "output.xlsx"
extract_data_from_pdf(pdf_path, output_excel)
