# pdf-analysis-app

This project is a web application that allows users to upload their university result PDFs for data analysis. The application processes the uploaded files and displays the analysis results on the same page.

## Project Structure

```
pdf-analysis-app
├── src
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── base.html
│   │   ├── index.html
│   │   └── results.html
│   ├── analysis
│   │   ├── __init__.py
│   │   └── pdf_analyzer.py
│   ├── app.py
│   └── utils
│       └── helpers.py
├── requirements.txt
└── README.md
```

## Features

- User-friendly interface for uploading PDF files.
- Data extraction and analysis from university result PDFs.
- Display of analysis results on the same page.

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd pdf-analysis-app
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python src/app.py
   ```

5. Open your web browser and go to `http://127.0.0.1:5000` to access the application.

## Usage

- Upload your university result PDF using the provided form on the main page.
- After uploading, the application will analyze the data and display the results on a new page.

## License

This project is licensed under the MIT License.