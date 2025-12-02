# 🔐 AI Selfie Verification System

An advanced AI-powered selfie verification system with real-time progress tracking, emotion detection, OCR, and WhatsApp integration.

## ✨ Features

### Core Verification
- **Liveness Detection**: Detects if the selfie is from a real person using blur detection
- **Face Matching**: Compares reference photo with selfie using histogram correlation
- **Live Webcam Capture**: Take selfies directly in the browser

### AI Analysis
- **Age & Gender Detection**: Estimates age and gender using DeepFace
- **Emotion Recognition**: Detects dominant emotion (Happy, Sad, Neutral, etc.)
- **Celebrity Lookalike**: Shows which celebrity you resemble
- **ID Card OCR**: Reads text from ID cards using EasyOCR to verify name match

### User Experience
- **Real-time Progress Bar**: Shows processing progress (0% → 100%) with time estimation
- **WhatsApp Integration**: Send verification reports or custom messages via WhatsApp
- **Wikipedia Integration**: Searches for the person's name and redirects to Wikipedia if found

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "new m"
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows: `.\venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🎯 Usage

1. **Run the application**
```bash
python app.py
```

2. **Open your browser**
Navigate to `http://127.0.0.1:5000`

3. **Verify Identity**
- Enter your full name
- Enter WhatsApp number (e.g., 919876543210)
- Upload reference photo (ID card)
- Click "Open Webcam" and capture selfie
- Click "Verify Identity"
- Watch the progress bar!

## 📦 Dependencies

- Flask - Web framework
- OpenCV - Image processing
- DeepFace - AI face analysis
- EasyOCR - Text extraction from images
- NumPy - Numerical operations
- Wikipedia - Wikipedia API integration

## 🏗️ Project Structure

```
.
├── app.py                 # Main Flask application
├── utils.py              # Helper functions for AI processing
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── templates/
│   ├── index.html       # Main verification page
│   └── profile.html     # Results/profile page
└── uploads/             # Temporary image storage
```

## 🔧 Technical Details

- **Backend**: Flask with Server-Sent Events (SSE) for real-time updates
- **AI Models**: DeepFace (VGG-Face), EasyOCR
- **Face Detection**: OpenCV Haar Cascade
- **Liveness**: Laplacian variance (blur detection)
- **Face Matching**: HSV histogram correlation

## 📱 WhatsApp Integration

The app uses `api.whatsapp.com` to send messages. Make sure to:
- Enter WhatsApp number in international format (e.g., 919876543210)
- Have WhatsApp Web/App installed

## 🐳 Docker Support

Build and run with Docker:
```bash
docker build -t selfie-verification .
docker run -p 5000:5000 selfie-verification
```

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Note

This is a development server. For production deployment, use a production WSGI server like Gunicorn.
