from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

import spacy
import os

nlp = spacy.load("./en_ner_biolp13cg_md-0.5.4")

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
        
        # Safely check for the existence of each nested key
        eligibility_text = None
        try:
            eligibility_text = data.get("protocolSection", {}).get("eligibilityModule", {}).get("eligibilityCriteria", "Eligibility criteria not available.")
        except KeyError:
            eligibility_text = "Eligibility criteria not available."

        return {
            "nct_id": nct_id,
            "title": data["protocolSection"]["identificationModule"]["briefTitle"],
            "eligibility": eligibility_text,
            "prior_therapies": extract_prior_therapies(eligibility_text)
        }
    
    except requests.RequestException as e:
        print("Request failed:", e)
        return None

def extract_prior_therapies(text):
    """Extracts required and excluded therapies from eligibility criteria text using NLP."""
    if not text:
        return [], []

    import re

    # Normalize line endings
    text = text.replace('\r\n', '\n')

    # Define regex pattern to extract inclusion and exclusion sections
    pattern = re.compile(
        r"(inclusion criteria.*?)(?:exclusion criteria|$)(.*)", 
        re.IGNORECASE | re.DOTALL
    )

    match = pattern.search(text)
    if match:
        inclusion_text = match.group(1).strip()
        exclusion_text = match.group(2).strip()
    else:
        inclusion_text = ""
        exclusion_text = ""

    inc_doc = nlp(inclusion_text)
    exc_doc = nlp(exclusion_text)

    required_therapies = [ent.text for ent in inc_doc.ents if ent.label_ == "SIMPLE_CHEMICAL"]
    excluded_therapies = [ent.text for ent in exc_doc.ents if ent.label_ == "SIMPLE_CHEMICAL"]

    return required_therapies, excluded_therapies
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
