import os
import PyPDF2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_url_path='/static')

def pdf_to_text(pdf_path):
    try:
        # Open the PDF file in read-binary mode
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            reader = PyPDF2.PdfReader(file)

            # Initialize an empty string to store the text content
            text_content = ''

            # Iterate over each page of the PDF
            for page in reader.pages:
                # Extract the text from the current page
                text_content += page.extract_text()

            return text_content

    except FileNotFoundError:
        print(f"File not found: {pdf_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Get a list of all uploaded files
        uploaded_files = request.files.getlist('file') 
        cv_texts = []

        # Save all uploaded files to the cv_database directory
        for file in uploaded_files:
            file_content = file.read()
            text_content = extract_text_from_pdf(file_content)
            if text_content:
                cv_texts.append(text_content)

        # Process the text content (e.g., extract skills and experience)
        extracted_data = process_text(cv_texts)

        return jsonify(extracted_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_text_from_pdf(pdf_content):
    try:
        # Create a PDF reader object
        reader = PyPDF2.PdfFileReader(pdf_content)

        # Initialize an empty string to store the text content
        text_content = ''

        # Iterate over each page of the PDF
        for page in range(reader.numPages):
            # Extract the text from the current page
            text_content += reader.getPage(page).extractText()

        return text_content

    except Exception as e:
        print(f"An error occurred while extracting text: {str(e)}")
        return None

def process_text(cv_texts):
    # Placeholder function for processing text (e.g., extracting skills and experience)
    # You can implement your text processing logic here
    extracted_data = []

    for text in cv_texts:
        # Example: Extract skills and experience
        skills = extract_skills(text)
        experience = extract_experience(text)

        extracted_data.append({'skills': skills, 'experience': experience})

    return extracted_data

def extract_skills(text):
    # Placeholder function for extracting skills from text
    # You can implement your skill extraction logic here
    # This is just a placeholder, replace it with your actual implementation
    return ['Skill 1', 'Skill 2', 'Skill 3']

def extract_experience(text):
    # Placeholder function for extracting experience from text
    # You can implement your experience extraction logic here
    # This is just a placeholder, replace it with your actual implementation
    return '5 years of experience in software development'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
