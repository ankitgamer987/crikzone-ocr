from flask import Flask, render_template, request, redirect, url_for, jsonify
import pytesseract
from PIL import Image
import os
import json
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load standings
def load_standings():
    with open('standings.json', 'r') as f:
        return json.load(f)

# Save standings
def save_standings(data):
    with open('standings.json', 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file", 400

    file = request.files['image']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    text = pytesseract.image_to_string(Image.open(filepath))
    
    # crude parsing - you can improve this
    if "MUMBAI INDIANS" in text.upper() and "PUNJAB KINGS" in text.upper():
        winner = "Mumbai Indians" if "won by" in text.lower() and "mumbai" in text.lower() else "Punjab Kings"
        data = load_standings()
        if winner not in data:
            data[winner] = {'wins': 0, 'losses': 0}
        data[winner]['wins'] += 1
        # update opponent
        opponent = "Punjab Kings" if winner == "Mumbai Indians" else "Mumbai Indians"
        if opponent not in data:
            data[opponent] = {'wins': 0, 'losses': 0}
        data[opponent]['losses'] += 1
        save_standings(data)
    else:
        winner = "Could not parse winner"
    
    return f"<h3>Result recorded for: {winner}</h3><a href='/'>Back</a>"

@app.route('/standings')
def standings():
    data = load_standings()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
