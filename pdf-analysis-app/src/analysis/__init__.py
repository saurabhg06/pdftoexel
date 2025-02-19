from typing import Dict, List
from analysis import extract_text_from_pdf, analyze_pdf_structure

import fitz  # PyMuPDF
def main():
    try:
        # Replace with your PDF file path
        pdf_path = "path/to/your/file.pdf"
        
        # Extract text from PDF
        text_content = extract_text_from_pdf(pdf_path)
        print("Extracted Text:")
        print(text_content)
        
        # Analyze PDF structure
        structure_info = analyze_pdf_structure(pdf_path)
        print("\nPDF Structure Information:")
        print(f"Number of pages: {structure_info['page_count']}")
        print(f"File size: {structure_info['file_size']} bytes")
        print("Metadata:", structure_info['metadata'])
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    main()
