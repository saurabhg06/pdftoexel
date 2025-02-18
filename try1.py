import pdfplumber

pdf_path = "results.pdf"  # Change this to your actual PDF file path

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        print(f"Page {page_num}:\n{text}\n" + "="*80)
