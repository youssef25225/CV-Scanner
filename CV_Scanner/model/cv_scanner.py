import numpy as np
import spacy
import pdfplumber
import os

def setup_nlp(patterns_path):
    nlp = spacy.load("en_core_web_sm")
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
    else:
        ruler = nlp.get_pipe("entity_ruler")
    
    if os.path.exists(patterns_path):
        ruler.from_disk(patterns_path)
    
    ruler.add_patterns([
        {"label": "SECTION", "pattern": [{"LOWER": "experience"}]},
        {"label": "SECTION", "pattern": [{"LOWER": "education"}]},
        {"label": "SECTION", "pattern": [{"LOWER": "projects"}]},
        {"label": "SECTION", "pattern": [{"LOWER": "certifications"}]},
        {"label": "SECTION", "pattern": [{"LOWER": "summary"}]},
    ])
    return nlp

def extract_text_from_pdf(path):
    with pdfplumber.open(path) as pdf:
        return " ".join(page.extract_text() or "" for page in pdf.pages)

def get_skills(text, nlp_model):
    doc = nlp_model(text)
    return {ent.text.lower() for ent in doc.ents if ent.label_ == "SKILL"}

def extract_sections(text, nlp_model):
    headers = {"EXPERIENCE", "EDUCATION", "PROJECTS", "CERTIFICATIONS", "SUMMARY"}
    doc = nlp_model(text.upper())
    found = sorted([(ent.start_char, ent.text) for ent in doc.ents if ent.label_ == "SECTION" and ent.text in headers])
    sections = {}
    for i, (start, name) in enumerate(found):
        end = found[i+1][0] if i+1 < len(found) else len(text)
        sections[name] = text[start:end].strip()
    return sections

def build_features(cv_text, jd_text, nlp_model):
    cv_sections = extract_sections(cv_text, nlp_model)
    cv_sk = get_skills(cv_text, nlp_model)
    jd_sk = get_skills(jd_text, nlp_model)
    overlap = cv_sk & jd_sk
    exp_overlap = overlap & get_skills(cv_sections.get("EXPERIENCE", ""), nlp_model)
    
    return np.array([
        len(overlap) / max(len(jd_sk), 1),
        len(exp_overlap) / max(len(overlap), 1),
        len(cv_sk)
    ])
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))