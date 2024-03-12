from flask import Flask, render_template, request, jsonify, send_file
import easyocr
from PIL import Image
import io
import numpy as np
from docx import Document
import tempfile
from flask_cors import CORS
from rembg import remove
from io import BytesIO


app = Flask(__name__)
CORS(app)

app = Flask(__name__)

reader = easyocr.Reader(['en'], gpu=False)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/writing', methods=['GET'])
def handwriting():
    return render_template('handwriting.html')

@app.route('/removebg', methods=['GET'])
def removebackground():
    return render_template('removebg.html')



@app.route('/scan', methods=['POST'])
def scan_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        image = Image.open(io.BytesIO(file.read()))
        results = reader.readtext(np.array(image))
        extracted_text = "\n".join([result[1] for result in results])

        # Create a Word document from the extracted text
        doc = Document()
        doc.add_paragraph(extracted_text)
        # Save the document to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        doc.save(temp_file.name)
        temp_file.close()

        return send_file(temp_file.name, as_attachment=True, download_name='extracted_text.docx')

@app.route('/handwriting', methods=['POST'])
def upload_writing():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        image = Image.open(io.BytesIO(file.read()))
        np_image = np.array(image)
        results = reader.readtext(np_image)
        extracted_texts = [result[1] for result in results]
        
        return jsonify({'text': extracted_texts})

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return "No image provided", 400
    
    file = request.files['image']
 
    if file.filename == '':
        return "No selected file", 400
    
    try:
        input_image = file.read()
        output_image = remove(input_image)

        return send_file(
            BytesIO(output_image),
            mimetype='image/png',
            as_attachment=True,
            download_name='no_bg.png'
        )
    except Exception as e:
        return f"Error processing image: {str(e)}", 500
if __name__ == '__main__':
    app.run(debug=True)