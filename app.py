from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    image_file = request.files['image']
    side = request.form['side']

    if image_file:
        path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(path)
        img = Image.open(path)
        text = pytesseract.image_to_string(img)

        if side == 'front':
            extracted = extract_front(text)
        else:
            extracted = extract_back(text)

        return render_template('index.html', data=extracted, side=side)

    return "❌ No image uploaded!"


def extract_front(text):
    import re
    name = re.findall(r'(?i)(?<=\n)[A-Z][a-z]+\s[A-Z][a-z]+', text)
    dob = re.findall(r'\d{2}/\d{2}/\d{4}', text)
    gender = "Male" if "MALE" in text.upper() else "Female" if "FEMALE" in text.upper() else "Not Found"
    aadhaar = re.findall(r'\d{4}\s\d{4}\s\d{4}', text)

    return {
        "name": name[0] if name else 'Not Found',
        "dob": dob[0] if dob else 'Not Found',
        "gender": gender,
        "aadhaar": aadhaar[0] if aadhaar else 'Not Found'
    }


def extract_back(text):
    import re
    normalized_text = " ".join(text.split())

    aadhaar = re.findall(r'\d{4}\s\d{4}\s\d{4}', normalized_text)
    aadhaar_number = aadhaar[0] if aadhaar else 'Not Found'

    match = re.search(r'S[/\\]O[:\s]+([^,]+),\s*(.+?)(?:\d{4}\s\d{4}\s\d{4}|VID|$)', normalized_text, re.IGNORECASE)
    if match:
        father = match.group(1).strip()
        address = match.group(2).strip()
    else:
        father = 'Not Found'
        address = 'Not Found'

    return {
        "father_name": father,
        "address": address,
        "aadhaar": aadhaar_number
    }


if __name__ == '__main__':
    app.run(debug=True)
