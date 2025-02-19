import PyPDF2
import pandas as pd
import re

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def parse_text_to_data(text):
    lines = text.split('\n')
    data = []
    current_student = {}
    
    for line in lines:
        if "Maharashtra State Board of Technical Education" in line:
            current_student['University Name'] = "Maharashtra State Board of Technical Education, Mumbai"
        elif "INSTITUTE :" in line:
            current_student['Institute Name'] = line.split("INSTITUTE :")[1].split("COURSE :")[0].strip()
            current_student['Course Name'] = line.split("COURSE :")[1].strip()
        elif "RESULT SHEET FOR THE FIRST SEMESTER (I) EXAMINATION HELD IN WINTER 2023" in line:
            current_student['Exam Session'] = "WINTER 2023"
        elif "Result Date :" in line:
            current_student['Result Date'] = line.split("Result Date :")[1].strip()
        elif re.match(r'\d{6}\s+\d{10}', line):
            parts = line.split()
            current_student['Seat Number'] = parts[0]
            current_student['Enrollment Number'] = parts[1]
            current_student['Student Name'] = ' '.join(parts[2:-3])
            current_student['Application Code'] = parts[-3]
            current_student['Total Marks'] = parts[-2]
            current_student['Result Status'] = parts[-1]
        elif re.match(r'\d{3}#|\d{3}\*', line):
            marks = line.split()
            subjects = ['ENG (ESE)', 'ENG (ISE)', 'ENG (Total)', 'ENG PR (ESE)', 'ENG PR (ISE)', 'ENG PR (Total)',
                        'BSC (ESE)', 'BSC (ISE)', 'BSC (Total)', 'BSC PR (ESE)', 'BSC PR (ISE)', 'BSC PR (Total)',
                        'BMS (ESE)', 'BMS (ISE)', 'BMS (Total)', 'ICT (ESE)', 'ICT (ISE)', 'ICT (Total)',
                        'EGM (ESE)', 'EGM (ISE)', 'EGM (Total)', 'WPM (ESE)', 'WPM (ISE)', 'WPM (Total)']
            for i, mark in enumerate(marks):
                current_student[subjects[i]] = mark
            data.append(current_student)
            current_student = {}
    
    return data

def save_to_excel(data, excel_path):
    df = pd.DataFrame(data)
    df.to_excel(excel_path, index=False)

def main():
    pdf_path = 'results.pdf'
    excel_path = 'results.xlsx'
    
    text = extract_text_from_pdf(pdf_path)
    data = parse_text_to_data(text)
    save_to_excel(data, excel_path)

if __name__ == "__main__":
    main()