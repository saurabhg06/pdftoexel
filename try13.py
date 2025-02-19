import pdfplumber
import pandas as pd
import re

# Function to extract student names from PDF
def extract_student_names(pdf_path, output_excel):
    names = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if text:
                names.extend(parse_names(text))
    
    df = pd.DataFrame(names, columns=["Student Name"])
    df.to_excel(output_excel, index=False)
    print(f"Student names successfully written to {output_excel}")

# Function to parse student names
def parse_names(text):
    names = []
    
    # Updated regex to capture student names only
    student_pattern = re.compile(r'\d{6}\s+\d{10}\s+([A-Z ]+?)\s+X Y [SW]\d{2}', re.DOTALL)
    
    for match in student_pattern.finditer(text):
        name = match.group(1).strip()
        names.append([name])
    
    return names

# Example Usage
pdf_path = "results.pdf"  # Replace with your PDF file
output_excel = "student_names.xlsx"
extract_student_names(pdf_path, output_excel)
