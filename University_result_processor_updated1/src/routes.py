from flask import Blueprint, render_template, request, jsonify, current_app, send_file, url_for
from werkzeug.utils import secure_filename
import os
from src.utils import process_pdf_file

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process PDF and get results
            results = process_pdf_file(filepath)
            if results:
                current_app.config['excel_files'] = results['excel_files']
            
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': True,
                'data': {
                    'toppers': results['toppers'],
                    'analysis': results['analysis']
                }
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

@main.route('/download/<file_type>')
def download_excel(file_type):
    """Handle Excel file downloads."""
    if 'excel_files' not in current_app.config:
        return jsonify({'error': 'No data available for download'}), 404
    
    excel_files = current_app.config['excel_files']
    if file_type not in excel_files:
        return jsonify({'error': 'Invalid file type'}), 400
    
    file_names = {
        'raw_data': 'extracted_data.xlsx',
        'toppers': 'toppers_list.xlsx',
        'analysis': 'result_analysis.xlsx'
    }
    
    return send_file(
        excel_files[file_type],
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=file_names[file_type]
    )

@main.route('/readme')
def readme():
    return render_template('readme.html')

@main.route('/caution')
def caution():
    return render_template('caution.html')

@main.route('/about')
def about():
    return render_template('about.html')