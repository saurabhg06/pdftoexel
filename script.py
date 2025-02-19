import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, render_template
import os

def extract_data_from_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    data.append(row)
    return pd.DataFrame(data)

def generate_result_analysis(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    plt.savefig("static/result_analysis.png", dpi=300, bbox_inches="tight")

def generate_toppers_image(df):
    img = Image.new('RGB', (800, 500), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    y_text = 50
    for index, row in df.iterrows():
        text = f"{row[0]} - {row[1]} - {row[2]} - {row[3]}"
        draw.text((50, y_text), text, fill=(0, 0, 0), font=font)
        y_text += 30
    img.save("static/class_toppers.png")

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(pdf_path)
            df = extract_data_from_pdf(pdf_path)
            generate_result_analysis(df)
            generate_toppers_image(df)
            return "Images Generated! Check static folder."
    return '''<form method='post' enctype='multipart/form-data'>
                <input type='file' name='file'>
                <input type='submit' value='Upload'>
              </form>'''

if __name__ == '__main__':
    app.run(debug=True)
