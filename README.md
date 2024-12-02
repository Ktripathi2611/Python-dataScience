# CyberShield AI Security Platform

A comprehensive AI-powered cybersecurity solution to protect users from digital threats like phishing, deep fakes, and online fraud.

## Features

### 1. Real-time Threat Detection
- URL scanning and analysis
- Phishing detection
- SSL security verification
- Website accessibility checks

### 2. Deep Fake Detection
- Image analysis
- Video frame extraction
- Audio processing
- Confidence scoring system

### 3. Security Dashboard
- Real-time security status monitoring
- Threat statistics
- Component status updates
- Recent activity tracking

### 4. User Education
- Security tips and best practices
- Interactive tutorials
- Real-time threat alerts
- Incident response guides

## Technology Stack

### Backend
- Python 3.12
- Flask 2.3.3
- SQLite Database
- JWT Authentication
- CORS enabled

### Frontend
- HTML5/CSS3
- Tailwind CSS
- JavaScript (ES6+)
- Font Awesome icons

### AI/ML Components
- TensorFlow
- NLTK for text processing
- OpenCV for image processing
- Librosa for audio analysis

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd AI-defence-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
set FLASK_APP=run.py
set FLASK_ENV=development
```

5. Initialize the database:
```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

6. Run the application:
```bash
flask run
```

The application will be available at `http://127.0.0.1:5000/`

## API Endpoints

### URL Scanning
- `POST /api/scan-url`
  - Body: `{"url": "https://example.com"}`
  - Returns: Security analysis results

### Image Analysis
- `POST /api/scan-image`
  - Body: Form data with image file
  - Returns: Deep fake detection results

### Security Status
- `GET /api/security-status`
  - Returns: Current security status and statistics

### Recent Activity
- `GET /api/recent-activity`
  - Returns: Latest security events and alerts

## Security Features

1. Input Validation
   - URL format verification
   - File type checking
   - Size limitations

2. Error Handling
   - Comprehensive error messages
   - Secure error logging
   - User-friendly notifications

3. Authentication
   - JWT-based authentication
   - Role-based access control
   - Secure token management

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TensorFlow team for AI/ML capabilities
- Flask team for the web framework
- Tailwind CSS for the UI framework
