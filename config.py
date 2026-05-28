import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max
    ALLOWED_EXTENSIONS = {'exe', 'dll', 'scr', 'bat', 'ps1', 'vbs', 'js', 'py', 
                          'doc', 'docx', 'pdf', 'txt', 'sh', 'bin', 'php', 'rb', 
                          'pl', 'zip', 'rar', '7z', 'tar', 'gz'}
    
    # Container settings
    MAX_CONTAINERS = int(os.environ.get('MAX_CONTAINERS', 10))
    CONTAINER_MEMORY_LIMIT = os.environ.get('CONTAINER_MEMORY_LIMIT', '256m')
    CONTAINER_CPU_LIMIT = 0.25
    CONTAINER_TIMEOUT = 15
    
    # Analysis settings
    STATIC_ANALYSIS = True
    BEHAVIORAL_ANALYSIS = True
    AI_ANALYSIS = True
    
    # Gemini AI Settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = 'gemma-3-27b-it'
    AI_TIMEOUT = 10
    
    # ZIP settings
    MAX_ZIP_SIZE = 500 * 1024 * 1024
    MAX_ZIP_FILES = 100
    
    # ===== NEW: URL Download Settings =====
    URL_DOWNLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'url_downloads')
    MAX_URL_DOWNLOAD_SIZE = 500 * 1024 * 1024  # 500MB
    URL_DOWNLOAD_TIMEOUT = 60  # seconds
    
    # File types to intercept
    INTERCEPT_EXTENSIONS = {
        '.exe', '.dll', '.scr', '.bat', '.ps1', '.vbs', '.js', '.py', 
        '.php', '.rb', '.pl', '.sh', '.zip', '.rar', '.7z', '.doc', 
        '.docx', '.xls', '.xlsx', '.pdf', '.jar', '.msi', '.apk', '.deb'
    }
    
    print(f"🔧 Configuration loaded:")
    print(f"  - Max containers: {MAX_CONTAINERS}")
    print(f"  - Container memory: {CONTAINER_MEMORY_LIMIT}")
    print(f"  - Max file size: {MAX_URL_DOWNLOAD_SIZE/(1024*1024)}MB")
    print(f"  - Gemini API Key: {'✅ Set' if GEMINI_API_KEY else '❌ Not set'}")
    print(f"  - Intercepting {len(INTERCEPT_EXTENSIONS)} file types")