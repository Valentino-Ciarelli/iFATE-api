import os
import json
from difflib import get_close_matches
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SecondUrl = "https://occupational-maps-api.instituteforapprenticeships.org/api/v1/GreenTheme/2?expand=occupation.overview%2Coccupation.salary"
ApiKey = os.environ.get("API_KEY")
CacheFile = "iFATE.json"

try:
    with open(CacheFile, 'r') as file:
        theme_cache = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    theme_cache = {}

def MatchThemes(ThemeName, pathways, threshold=0.65):
    matches = get_close_matches(ThemeName.lower(), pathways, n=len(pathways), cutoff=threshold)
    return matches

def FetchPathwaysFromAPI():
    response = requests.get(SecondUrl, headers={"X-API-KEY": ApiKey})
    if response.status_code == 200:
        data = response.json()
        with open(CacheFile, 'w') as file:
            json.dump(data, file, indent=4)
        return data
    else:
        return None

@app.route('/pathways', methods=['GET'])
def pathways():
    ThemeName = request.args.get('theme', None)

    if not theme_cache:
        data = FetchPathwaysFromAPI()
        if not data:
            return jsonify({"error": "Failed to fetch data from the API."}), 500

    if ThemeName:
        matching_pathways = [
            pathway for pathway in theme_cache.get("pathways", [])
            if MatchThemes(ThemeName, [pathway["name"]])
        ]
        if matching_pathways:
            return jsonify(matching_pathways)
        else:
            return jsonify({"message": f"No pathways found for theme: {ThemeName}"})
    else:
        return jsonify(theme_cache.get("pathways", []))

if __name__ == '__main__':
    app.run(debug=True)
