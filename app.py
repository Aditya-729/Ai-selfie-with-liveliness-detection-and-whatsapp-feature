import os
import base64
import time
import uuid
from flask import Flask, render_template, request, jsonify, redirect, Response
from utils import check_liveness, get_face_encoding, compare_faces, analyze_face, extract_text, find_celebrity_lookalike, get_wikipedia_url
import cv2
import numpy as np
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Progress tracking
progress_data = {}

def update_progress(session_id, percent, message):
    """Update progress for a session"""
    progress_data[session_id] = {
        'percent': percent,
        'message': message,
        'timestamp': time.time()
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress/<session_id>')
def progress(session_id):
    """SSE endpoint for progress updates"""
    def generate():
        start_time = time.time()
        last_percent = 0
        
        while True:
            if session_id in progress_data:
                data = progress_data[session_id]
                percent = data['percent']
                message = data['message']
                
                # Calculate estimated time remaining
                elapsed = time.time() - start_time
                if percent > 0 and percent < 100:
                    total_estimated = (elapsed / percent) * 100
                    remaining = total_estimated - elapsed
                else:
                    remaining = 0
                
                yield f"data: {json.dumps({'percent': percent, 'message': message, 'remaining': int(remaining)})}\n\n"
                
                if percent >= 100:
                    # Clean up
                    del progress_data[session_id]
                    break
                    
                last_percent = percent
            
            time.sleep(0.5)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/verify', methods=['POST'])
def verify():
    session_id = request.form.get('session_id', str(uuid.uuid4()))
    name = request.form.get('name')
    whatsapp = request.form.get('whatsapp')
    
    update_progress(session_id, 0, 'Starting verification...')
    
    # Handle Reference Image
    if 'reference' in request.files and request.files['reference'].filename != '':
        reference_file = request.files['reference']
        ref_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reference.jpg')
        reference_file.save(ref_path)
    else:
        return jsonify({'result': 'Error', 'message': 'Reference image required.'}), 400

    # Handle Selfie (File or Base64)
    selfie_path = os.path.join(app.config['UPLOAD_FOLDER'], 'selfie.jpg')
    if 'selfie' in request.files and request.files['selfie'].filename != '':
        selfie_file = request.files['selfie']
        selfie_file.save(selfie_path)
    elif 'selfie_base64' in request.form and request.form['selfie_base64'] != '':
        # Decode Base64
        data = request.form['selfie_base64']
        header, encoded = data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        with open(selfie_path, 'wb') as f:
            f.write(binary_data)
    else:
        return jsonify({'result': 'Error', 'message': 'Selfie required.'}), 400

    # 1. Liveness Check (on Selfie)
    update_progress(session_id, 20, 'Checking liveness...')
    is_live, liveness_score, liveness_msg = check_liveness(selfie_path)

    # 2. Face Matching
    update_progress(session_id, 40, 'Detecting faces...')
    ref_encoding = get_face_encoding(ref_path)
    selfie_encoding = get_face_encoding(selfie_path)

    if ref_encoding is None:
        update_progress(session_id, 100, 'Error')
        return jsonify({'result': 'Error', 'message': 'No face found in reference photo.'})
    if selfie_encoding is None:
        update_progress(session_id, 100, 'Error')
        return jsonify({'result': 'Error', 'message': 'No face found in selfie.'})

    match = compare_faces(ref_encoding, selfie_encoding)

    # 3. Advanced Features
    # OCR
    update_progress(session_id, 60, 'Reading ID card text...')
    ocr_text = extract_text(ref_path)
    name_match = name.lower() in ocr_text.lower() if name else False
    
    # AI Analysis
    update_progress(session_id, 80, 'Analyzing face attributes...')
    analysis = analyze_face(selfie_path)
    
    # Celebrity Lookalike (if not matched or just for fun)
    celebrity = find_celebrity_lookalike(selfie_path)
    
    # Wikipedia
    wiki_url = get_wikipedia_url(name) if name else None

    # 4. Determine Final Result
    update_progress(session_id, 100, 'Complete!')
    
    if match:
        if is_live:
            result = "Matched + Real"
            status = "success"
        else:
            result = "Matched but seems Fake"
            status = "warning"
    else:
        result = "Not Matched"
        status = "error"

    return jsonify({
        'result': result,
        'message': f"{liveness_msg} (Score: {liveness_score:.2f})",
        'status': status,
        'analysis': analysis,
        'ocr_match': name_match,
        'celebrity': celebrity,
        'wiki_url': wiki_url,
        'name': name,
        'whatsapp': whatsapp
    })

@app.route('/profile/<name>')
def profile(name):
    # Get data from query params
    data = {
        'name': name,
        'whatsapp': request.args.get('whatsapp'),
        'result': request.args.get('result'),
        'status': request.args.get('status'),
        'age': request.args.get('age'),
        'gender': request.args.get('gender'),
        'emotion': request.args.get('emotion'),
        'celebrity': request.args.get('celebrity'),
        'ocr_match': request.args.get('ocr_match') == 'true'
    }
    return render_template('profile.html', **data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

