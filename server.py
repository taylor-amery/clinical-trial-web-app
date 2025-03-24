from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
import requests

def fetch_trial_data(nct_id):
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    
    try:
        response = requests.get(url)
        print("Status Code:", response.status_code)  # Debugging
        
        if response.status_code != 200:
            print("Error: Received non-200 status code")
            return None
        
        # Print raw text response for debugging
        print("Raw Response Text:", response.text)
        
        try:
            data = response.json()
            print("Parsed JSON:", data)  # Debugging
            return data
        except ValueError:
            print("Error: Invalid JSON response from API")
            return None
        
    except requests.RequestException as e:
        print("Request failed:", e)
        return None


@app.route('/get_trial', methods=['GET'])
def get_trial():
    nct_number = request.args.get('nct')
    if not nct_number:
        return jsonify({"error": "No NCT number provided"}), 400
    
    data = fetch_trial_data(nct_number)
    return jsonify(data)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

