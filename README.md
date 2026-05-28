File Sandbox & Malware Analysis Tool
A powerful, Flask-based web application and Chrome extension designed for secure file analysis, threat detection, and AI-powered sanitization.

🚀 Features
Static Analysis: In-depth inspection of uploaded files for suspicious patterns and behaviors.
Batch Processing: Upload ZIP files to analyze multiple files simultaneously.
URL Interceptor: A Chrome extension that intercepts downloads and sends them to the sandbox for analysis before they reach your system.
AI Sanitization: Uses Google Gemini to analyze and sanitize potentially malicious script files (Python, JS, etc.).
Docker Support: Easy deployment using Docker and Docker Compose.
Real-time Monitoring: Progress tracking and detailed threat reports for every analysis.
🛠️ Tech Stack
Backend: Python, Flask
Frontend: HTML5, Vanilla CSS, JavaScript
AI Engine: Google Gemini API
Containerization: Docker, Docker Compose
Browser Integration: Chrome Extension (JavaScript)
📋 Prerequisites
Python 3.9+
Docker (optional, for containerized deployment)
Google Gemini API Key (for sanitization features)
⚙️ Setup & Installation
Clone the repository:

git clone <your-repo-url>
cd file-sandbox
Configure Environment Variables: Create a .env file in the root directory:

GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
Running with Docker (Recommended):

docker-compose up --build
Running Locally:

pip install -r requirements.txt
python app.py
🧩 Chrome Extension Setup
Open Chrome and navigate to chrome://extensions/.
Enable Developer mode.
Click Load unpacked and select the extension folder from this project.
The extension will now intercept downloads of specified file types and send them to your local sandbox.
🛡️ License
This project is licensed under the MIT License.

