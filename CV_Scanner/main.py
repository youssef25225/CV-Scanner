from flask import Flask, render_template, request, jsonify
import os
import pickle
import numpy as np
from werkzeug.utils import secure_filename
from model.cv_scanner import extract_text_from_pdf, build_features, get_skills, setup_nlp

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

patterns_path = os.path.join("data", "jz.jsonl")
nlp = setup_nlp(patterns_path)

try:
    with open("cv_model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'cv_file' not in request.files:
            return jsonify({'error': 'No CV file uploaded'}), 400
        
        cv_file = request.files['cv_file']
        job_description = request.form.get('job_description', '')
        
        if cv_file.filename == '' or not job_description.strip():
            return jsonify({'error': 'Missing file or description'}), 400
        
        if cv_file and allowed_file(cv_file.filename):
            filename = secure_filename(cv_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            cv_file.save(filepath)
            
            cv_text = extract_text_from_pdf(filepath)
            
            cv_skills = get_skills(cv_text, nlp)
            jd_skills = get_skills(job_description, nlp)
            
            matching_skills = cv_skills & jd_skills
            if len(jd_skills) > 0:
                match_percentage = (len(matching_skills) / len(jd_skills)) * 100
            else:
                match_percentage = 0
            
            result = {
                'match_percentage': round(match_percentage, 2),
                'matching_skills': list(matching_skills),
                'missing_skills': list(jd_skills - cv_skills),
                'total_cv_skills': len(cv_skills),
                'total_jd_skills': len(jd_skills)
            }
            
            os.remove(filepath)
            return jsonify(result)
            
        return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)