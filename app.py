# app.py

import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import PyPDF2
from pptx import Presentation

# Load environment variables from .env file
load_dotenv()

# Configure the Google AI API key
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("ERROR: Google API Key not found. Please set it in your .env file.")
    exit()

# Initialize the Flask app
app = Flask(__name__)

# Configure the upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_text_from_files(file_paths):
    full_text = ""
    for file_path in file_paths:
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        full_text += page.extract_text() + "\n"
            elif file_path.endswith('.pptx'):
                pres = Presentation(file_path)
                for slide in pres.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            full_text += shape.text + "\n"
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            full_text += f"\n[Error processing file: {os.path.basename(file_path)}]\n"
    return full_text

# --- NEW FUNCTION TO CALL THE GEMINI AI ---
def generate_study_guide_from_ai(text):
    """
    Sends the extracted text to the Gemini model and returns the generated study guide.
    """
    # This is the prompt that instructs the AI on what to do.
    prompt = """
    You are an expert academic assistant. Based on the following text from course materials, please create a concise study guide. 
    The study guide should include three sections:
    1. A 'Key Concepts' section with bullet points summarizing the main topics.
    2. A 'Key Terms' section listing important vocabulary with their definitions.
    3. A 'Practice Questions' section with 3-5 short-answer questions that could appear on an exam.

    Here is the content:
    ---
    """ + text

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI generation failed: {e}")
        return "Error: Could not generate the study guide from the AI. Please check your API key and server logs."

# This is the main route that displays the webpage
@app.route('/')
def index():
    return render_template('index.html')

# This route will handle the file uploads and AI processing
@app.route('/generate-guide', methods=['POST'])
def generate_guide():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('files')
    if len(files) == 0 or files[0].filename == '':
        return jsonify({"error": "No selected files"}), 400

    saved_file_paths = []
    for file in files:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        saved_file_paths.append(file_path)
    
    extracted_text = extract_text_from_files(saved_file_paths)
    if not extracted_text or extracted_text.isspace():
        return jsonify({"error": "Could not extract text from the uploaded files. Are they valid .pdf or .pptx files with text?"})

    # --- FINAL CHANGE: CALL THE AI FUNCTION ---
    # Instead of sending the raw text, we send the AI-generated guide
    study_guide = generate_study_guide_from_ai(extracted_text)
    
    # We now send the final study_guide to the frontend
    return jsonify({"study_guide": study_guide})

# This allows you to run the app directly
if __name__ == '__main__':
    app.run(debug=True)