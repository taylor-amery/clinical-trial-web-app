from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Function to fetch trial data from ClinicalTrials.gov
def fetch_trial_data(nct_number):
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_number}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Returns the JSON response
    else:
        return {"error": f"Trial {nct_number} not found"}

# API Endpoint to get trial data
@app.route('/get_trial', methods=['GET'])
def get_trial():
    nct_number = request.args.get('nct')
    if not nct_number:
        return jsonify({"error": "No NCT number provided"}), 400
    
    data = fetch_trial_data(nct_number)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
