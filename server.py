from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

import spacy
from pathlib import Path

model_path = Path(__file__).parent / "en_core_sci_sm"
nlp = spacy.load(model_path)

app = Flask(__name__)
CORS(app)

def fetch_trial_data(nct_id):
    """Fetches trial data from ClinicalTrials.gov API and extracts eligibility criteria."""
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Extract eligibility criteria if available
        eligibility_text = None
        try:
            eligibility_text = data["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
        except KeyError:
            eligibility_text = "Eligibility criteria not available."

        return {
            "nct_id": nct_id,
            "eligibility": eligibility_text,
            "prior_therapies": extract_prior_therapies(eligibility_text)
        }
    
    except requests.RequestException as e:
        print("Request failed:", e)
        return None

def extract_prior_therapies(text):
    """Extracts prior therapies using NLP from eligibility criteria."""
    if not text:
        return []
    
    doc = nlp(text)
    therapies = [ent.text for ent in doc.ents if ent.label_ in ["TREATMENT", "CHEMICAL"]]
    
    return list(set(therapies))  # Remove duplicates
@app.route('/')
def home():
    return "Welcome to my API"

@app.route('/get_trial', methods=['GET'])
def get_trial():
    """Fetches trial data, extracts eligibility criteria, and applies NLP."""
    nct_number = request.args.get('nct')
    if not nct_number:
        return jsonify({"error": "No NCT number provided"}), 400
    
    trial_data = fetch_trial_data(nct_number)
    if trial_data is None:
        return jsonify({"error": "Trial not found"}), 404
    
    return jsonify(trial_data)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
