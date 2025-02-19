from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from pdf_converter import convert_pdf_to_excel

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        
        # Convert PDF to Excel
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                os.path.splitext(filename)[0] + '.xlsx')
        convert_pdf_to_excel(pdf_path, excel_path)
        
        return send_file(excel_path, as_attachment=True)
    
    return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)