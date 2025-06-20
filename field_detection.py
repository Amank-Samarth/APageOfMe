import spacy
from collections import Counter

# Load spaCy English model
nlp = spacy.load('en_core_web_sm')

# Simple mapping from keywords to fields (expand as needed)
FIELD_KEYWORDS = {
    'Data Science': ['machine learning', 'data analysis', 'statistics', 'deep learning', 'python'],
    'Web Development': ['django', 'flask', 'react', 'javascript', 'html', 'css'],
    'Android Development': ['android', 'kotlin', 'java', 'android studio'],
    'iOS Development': ['ios', 'swift', 'objective-c', 'xcode'],
    'UI-UX': ['ux', 'ui', 'figma', 'adobe xd', 'wireframes', 'user research'],
    'Finance': ['accounting', 'finance', 'auditing', 'tax', 'investment', 'banking'],
    'Marketing': ['marketing', 'seo', 'content', 'brand', 'advertising', 'analytics'],
    'Education': ['teaching', 'curriculum', 'lesson', 'education', 'instructor', 'trainer'],
    'Healthcare': ['nurse', 'doctor', 'medical', 'healthcare', 'clinic', 'patient'],
    # Add more fields as needed
}

KEYWORD_TO_FIELD = {kw: field for field, kws in FIELD_KEYWORDS.items() for kw in kws}

def extract_field_and_titles(resume_text):
    doc = nlp(resume_text.lower())
    # Extract possible skills and job titles
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    field_counter = Counter()
    found_titles = []
    for token in tokens:
        if token in KEYWORD_TO_FIELD:
            field_counter[KEYWORD_TO_FIELD[token]] += 1
    # Try to extract job titles using NER
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'WORK_OF_ART', 'PRODUCT', 'PERSON']:
            continue
        if ent.label_ in ['TITLE', 'JOB', 'POSITION'] or 'engineer' in ent.text or 'manager' in ent.text or 'developer' in ent.text or 'teacher' in ent.text:
            found_titles.append(ent.text)
    # Fallback: look for common job title words in tokens
    for token in tokens:
        if token in ['engineer', 'developer', 'manager', 'teacher', 'designer', 'analyst', 'consultant', 'nurse', 'doctor', 'accountant', 'officer', 'specialist', 'executive', 'director', 'coordinator', 'scientist', 'technician', 'instructor', 'trainer']:
            found_titles.append(token)
    # Most common field
    detected_field = field_counter.most_common(1)[0][0] if field_counter else None
    return detected_field, list(set(found_titles))
