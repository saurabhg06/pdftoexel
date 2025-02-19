from flask import Flask, request, jsonify
import PyPDF2
import pandas as pd
import re
from io import BytesIO

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def parse_result_data(text):
    """Parse extracted text into structured data
    This is a simplified version - you'll need to adjust the regex patterns
    based on your actual PDF format
    """
    # Example pattern - adjust based on your PDF structure
    pattern = r'(\w+)\s+(\w+\s+\w+)\s+(\d)\s+(\w+)\s+(\d+)\s+([A-F])\s+(Pass|Fail)'
    matches = re.finditer(pattern, text)
    
    data = []
    for match in matches:
        data.append({
            'student_id': match.group(1),
            'name': match.group(2),
            'semester': match.group(3),
            'subject': match.group(4),
            'marks': match.group(5),
            'grade': match.group(6),
            'status': match.group(7)
        })
    
    return data

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.pdf'):
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        
        # Parse the text into structured data
        data = parse_result_data(text)
        
        # Convert to DataFrame and perform analysis
        df = pd.DataFrame(data)
        
        # Basic analysis
        analysis = {
            'total_students': len(df['student_id'].unique()),
            'pass_percentage': (len(df[df['status'] == 'Pass']) / len(df) * 100),
            'subject_averages': df.groupby('subject')['marks'].mean().to_dict(),
            'grade_distribution': df['grade'].value_counts().to_dict()
        }
        
        # Save to CSV (optional)
        df.to_csv('results.csv', index=False)
        
        return jsonify({
            'status': 'success',
            'data': data,
            'analysis': analysis
        })
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    try:
        df = pd.read_csv('results.csv')
        
        analysis = {
            'performance_by_subject': df.groupby('subject').agg({
                'marks': ['mean', 'min', 'max'],
                'status': lambda x: (x == 'Pass').mean() * 100
            }).to_dict(),
            'top_performers': df[df['marks'] >= 90]['name'].unique().tolist(),
            'subjects_needing_attention': df[df['status'] == 'Fail']['subject'].unique().tolist()
        }
        
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)