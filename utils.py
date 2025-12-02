import cv2
import numpy as np
import os
from deepface import DeepFace
import easyocr
import wikipedia
import random

# Initialize EasyOCR Reader (English)
reader = easyocr.Reader(['en'], gpu=False)

# Liveness Threshold
LIVENESS_THRESHOLD = 100.0

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def check_liveness(image_path_or_array):
    """
    Checks liveness using Laplacian variance (blur detection).
    Returns: (is_live, score, message)
    """
    if isinstance(image_path_or_array, str):
        image = cv2.imread(image_path_or_array)
    else:
        image = image_path_or_array
    
    if image is None:
        return False, 0, "Could not load image."

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()

    is_live = score > LIVENESS_THRESHOLD
    msg = f"Liveness Confirmed (Score: {score:.2f})" if is_live else f"Liveness Failed (Score: {score:.2f})"

    return is_live, score, msg

def get_face_encoding(image_path_or_array):
    """
    Returns the face histogram (HSV) for an image.
    Uses Haar Cascade for detection.
    """
    if isinstance(image_path_or_array, str):
        image = cv2.imread(image_path_or_array)
    else:
        image = image_path_or_array
    
    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return None

    # Take first face
    (x, y, w, h) = faces[0]
    face_roi = image[y:y+h, x:x+w]

    # Convert to HSV
    hsv_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)

    # Calculate Histogram
    hist = cv2.calcHist([hsv_face], [0, 1], None, [50, 60], [0, 180, 0, 256])

    # Normalize
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

    return hist

def compare_faces(known_encoding, check_encoding):
    """
    Compares two face histograms using Correlation.
    Returns True if correlation is high enough.
    """
    if known_encoding is None or check_encoding is None:
        return False
    
    score = cv2.compareHist(known_encoding, check_encoding, cv2.HISTCMP_CORREL)
    MATCH_THRESHOLD = 0.5

    return score > MATCH_THRESHOLD

def analyze_face(image_path):
    """
    Uses DeepFace to analyze age, gender, and emotion.
    """
    try:
        objs = DeepFace.analyze(img_path = image_path, 
                actions = ['age', 'gender', 'emotion'],
                enforce_detection=False
        )
        # DeepFace returns a list of dicts
        if objs:
            obj = objs[0]
            return {
                'age': obj.get('age'),
                'gender': obj.get('dominant_gender'),
                'emotion': obj.get('dominant_emotion')
            }
    except Exception as e:
        print(f"DeepFace Error: {e}")
    return None

def extract_text(image_path):
    """
    Uses EasyOCR to extract text from an image.
    """
    try:
        result = reader.readtext(image_path, detail=0)
        return " ".join(result)
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def find_celebrity_lookalike(image_path):
    """
    Mock function for celebrity lookalike.
    """
    # In a real app, we'd use DeepFace.find() against a celebrity DB.
    # For now, we'll return a random "fun" result.
    celebs = ["Elon Musk", "Brad Pitt", "Angelina Jolie", "Robert Downey Jr.", "Scarlett Johansson", "The Rock"]
    return random.choice(celebs)

def get_wikipedia_url(name):
    """
    Searches Wikipedia for the name.
    """
    try:
        # Search for the page
        results = wikipedia.search(name)
        if results:
            page = wikipedia.page(results[0], auto_suggest=False)
            return page.url
    except Exception as e:
        print(f"Wiki Error: {e}")
    return None
