import pdfplumber
import pandas as pd

pdf_path = "results.pdf"  # Your uploaded PDF file
data = []

# Open the PDF and extract tables
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_table()
        if tables:
            for row in tables:
                data.append(row)  # Append each row of the table

# Convert extracted data to a Pandas DataFrame
df = pd.DataFrame(data)

# Save as CSV
csv_path = "results.csv"
df.to_csv(csv_path, index=False)

print(f"CSV saved at {csv_path}")
