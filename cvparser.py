import os
import PyPDF2
from flask import Flask, request, jsonify, render_template, send_file, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def get_best_matching_cv(description, cv_texts, cv_paths):
    best_cv = None
    best_similarity_score = 0

    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the texts into TF-IDF feature vectors
    tfidf_matrix = vectorizer.fit_transform(cv_texts)

    # Calculate the similarity score between the description and each CV
    for i, pdf_text in enumerate(cv_texts):
        similarity_score = cosine_similarity(tfidf_matrix[i], vectorizer.transform([description]))[0][0]

        print(f"CV {i+1} - Similarity Score: {similarity_score}")

        # Check if the current CV has a higher similarity score
        if similarity_score > best_similarity_score:
            best_similarity_score = similarity_score
            best_cv = cv_paths[i]

    return best_cv, best_similarity_score

def download_file():
    try:
        file_name = 'your_file.pdf'  # Replace with the actual file name
        file_path = os.path.join('cv_database', file_name)  # Update with the correct path

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        description = request.form.get('description', '')
        # Get a list of all uploaded files
        uploaded_files = request.files.getlist('file') 
        cv_folder_path = 'cv_database/'  
        uploaded_file_paths = []

        # Save all uploaded files to the cv_database directory
        for file in uploaded_files:
            file_path = os.path.join(cv_folder_path, file.filename)
            file.save(file_path)
            uploaded_file_paths.append(file_path)

        # Get the list of PDF files in the folder
        files_in_folder = os.listdir(cv_folder_path)
        cv_paths = [os.path.join(cv_folder_path, file) for file in files_in_folder if file.lower().endswith('.pdf')]

        cv_texts = []
        for pdf_path in cv_paths:
            pdf_text = pdf_to_text(pdf_path)
            if pdf_text:
                cv_texts.append(pdf_text)

        best_cv, best_similarity_score = get_best_matching_cv(description, cv_texts, cv_paths)

        if best_cv:
            result = {
                'best_cv': best_cv,
                'similarity_score': best_similarity_score
            }
        else:
            result = {'message': 'No valid CV found.'}

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['GET'])
def download_file():
    try:
        # Get the provided file name from query parameter
        file_name = request.args.get('filename')  
        # attach filename with the folder path to access our desired resume
        file_path = os.path.join('cv_database', file_name)  

        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    # where the resume's are stored.
    cv_folder_path = 'cv_database/'  
    files_in_folder = os.listdir(cv_folder_path)
    cv_paths = [os.path.join(cv_folder_path, file) for file in files_in_folder if file.lower().endswith('.pdf')]

    app.run(host='0.0.0.0', port=5000,debug=True)