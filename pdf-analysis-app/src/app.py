from flask import Flask, render_template, request
from analysis.pdf_analyzer import analyze_pdf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        return 'No file part', 400
    file = request.files['pdf_file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        analysis_result = analyze_pdf(file)
        return render_template('results.html', result=analysis_result)

if __name__ == '__main__':
    app.run(debug=True)