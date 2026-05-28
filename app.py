from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
import threading
import time
import traceback
import requests
from urllib.parse import urlparse
import magic
from dotenv import load_dotenv

load_dotenv()

from config import Config
from analyzer import FileAnalyzer
from zip_handler import ZIPHandler
from queue_manager import AnalysisQueueManager
from sanitizer import CodeSanitizer

app = Flask(__name__)
app.config.from_object(Config)

# Ensure all folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'extracted'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'sanitized'), exist_ok=True)
os.makedirs(app.config['URL_DOWNLOAD_FOLDER'], exist_ok=True)  # NEW
os.chmod(app.config['UPLOAD_FOLDER'], 0o777)

# Initialize components
zip_handler = ZIPHandler(app.config['UPLOAD_FOLDER'])
queue_manager = AnalysisQueueManager(max_workers=Config.MAX_CONTAINERS)
queue_manager.start()

# Initialize sanitizer
sanitizer = None
if Config.GEMINI_API_KEY:
    sanitizer = CodeSanitizer(Config.GEMINI_API_KEY, Config.GEMINI_MODEL)

# Store active analyses
active_analyses = {}
batch_analyses = {}

# ===== NEW: URL Download Endpoint =====

@app.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    """
    Download and analyze a file from URL
    This is called by the Chrome extension
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url')
        filename = data.get('filename')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Generate unique ID
        analysis_id = str(uuid.uuid4())
        
        # Get filename from URL if not provided
        if not filename:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or 'download.bin'
        
        # Clean filename
        filename = secure_filename(filename)
        
        # Check file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in Config.INTERCEPT_EXTENSIONS:
            return jsonify({
                'decision': 'allow',
                'message': f'File type {ext} not monitored',
                'url': url
            })
        
        # Initialize analysis status
        active_analyses[analysis_id] = {
            'status': 'downloading',
            'progress': 0,
            'stage': 'Downloading file from URL',
            'filename': filename,
            'url': url,
            'start_time': datetime.now().isoformat(),
            'type': 'url_download',
            'file_path': None
        }
        
        # Start download and analysis in background
        thread = threading.Thread(
            target=download_and_analyze_url,
            args=(analysis_id, url, filename)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'status': 'downloading',
            'message': 'Download started, analysis will begin automatically'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

def download_and_analyze_url(analysis_id, url, filename):
    """Download file from URL and analyze it"""
    try:
        if os.path.exists('/.dockerenv'):
            # Replace localhost/127.0.0.1 with host.docker.internal
            if '127.0.0.1' in url:
                url = url.replace('127.0.0.1', 'host.docker.internal')
                print(f"🔄 Converted URL for Docker: {url}")
            if 'localhost' in url:
                url = url.replace('localhost', 'host.docker.internal')
                print(f"🔄 Converted URL for Docker: {url}")
        # Update status
        active_analyses[analysis_id].update({
            'status': 'downloading',
            'progress': 10,
            'stage': 'Connecting to server'
        })
        
        # Download file with progress tracking
        response = requests.get(url, stream=True, timeout=Config.URL_DOWNLOAD_TIMEOUT)
        response.raise_for_status()
        
        # Get file size
        file_size = int(response.headers.get('content-length', 0))
        active_analyses[analysis_id]['file_size'] = file_size
        
        # Check file size
        if file_size > Config.MAX_URL_DOWNLOAD_SIZE:
            active_analyses[analysis_id].update({
                'status': 'failed',
                'error': f'File too large (max {Config.MAX_URL_DOWNLOAD_SIZE/(1024*1024)}MB)'
            })
            return
        
        # Save file to URL download folder
        safe_filename = f"{analysis_id}_{filename}"
        file_path = os.path.join(app.config['URL_DOWNLOAD_FOLDER'], safe_filename)
        
        downloaded = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if file_size > 0:
                        progress = 10 + int((downloaded / file_size) * 40)  # 10-50% progress
                        active_analyses[analysis_id].update({
                            'progress': progress,
                            'stage': f'Downloading: {downloaded/(1024*1024):.1f}MB / {file_size/(1024*1024):.1f}MB'
                        })
        
        active_analyses[analysis_id].update({
            'status': 'downloaded',
            'progress': 50,
            'stage': 'Download complete, starting analysis',
            'file_path': file_path
        })
        
        # Now analyze the file using your existing analyzer
        run_single_analysis(analysis_id, file_path, filename)
        
    except requests.exceptions.RequestException as e:
        active_analyses[analysis_id].update({
            'status': 'failed',
            'error': f'Download failed: {str(e)}'
        })
    except Exception as e:
        active_analyses[analysis_id].update({
            'status': 'failed',
            'error': str(e)
        })

# ===== Keep all your existing routes exactly as they are =====

@app.route('/')
def index():
    return render_template('index.html')

# Add this after app initialization
@app.after_request
def add_header(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/api/debug/analyses')
def debug_analyses():
    """Debug endpoint to see all active analyses"""
    return jsonify({
        'active_analyses': {k: {
            'status': v.get('status'),
            'filename': v.get('filename'),
            'progress': v.get('progress')
        } for k, v in active_analyses.items()},
        'batch_analyses': list(batch_analyses.keys())
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint for extension"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    """Handle file upload (existing)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if it's a ZIP file
        filename = file.filename.lower()
        if filename.endswith('.zip'):
            return handle_zip_upload(file)
        
        # Regular file handling
        return handle_single_file(file)
        
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

def handle_single_file(file):
    """Handle single file upload"""
    analysis_id = str(uuid.uuid4())
    original_filename = secure_filename(file.filename)
    
    filename = f"{analysis_id}_{original_filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save file
    chunk_size = 8192
    with open(file_path, 'wb') as f:
        while True:
            chunk = file.stream.read(chunk_size)
            if len(chunk) == 0:
                break
            f.write(chunk)
    
    file_size = os.path.getsize(file_path)
    
    active_analyses[analysis_id] = {
        'status': 'queued',
        'progress': 0,
        'stage': 'Queued for analysis',
        'filename': original_filename,
        'file_size': file_size,
        'start_time': datetime.now().isoformat(),
        'type': 'single',
        'file_path': file_path
    }
    
    thread = threading.Thread(
        target=run_single_analysis,
        args=(analysis_id, file_path, original_filename)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'analysis_id': analysis_id,
        'status': 'started',
        'filename': original_filename,
        'file_size': file_size,
        'type': 'single'
    })

def handle_zip_upload(file):
    """Handle ZIP file upload"""
    batch_id = str(uuid.uuid4())
    original_filename = secure_filename(file.filename)
    zip_filename = f"{batch_id}_{original_filename}"
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    
    # Save ZIP
    chunk_size = 8192
    with open(zip_path, 'wb') as f:
        while True:
            chunk = file.stream.read(chunk_size)
            if len(chunk) == 0:
                break
            f.write(chunk)
    
    batch_analyses[batch_id] = {
        'status': 'extracting',
        'progress': 0,
        'stage': 'Extracting ZIP file',
        'filename': original_filename,
        'file_size': os.path.getsize(zip_path),
        'start_time': datetime.now().isoformat(),
        'type': 'zip',
        'total_files': 0,
        'completed_files': 0,
        'failed_files': 0,
        'files': {}
    }
    
    thread = threading.Thread(
        target=process_zip_file,
        args=(batch_id, zip_path)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'analysis_id': batch_id,
        'status': 'extracting',
        'filename': original_filename,
        'file_size': os.path.getsize(zip_path),
        'type': 'zip'
    })

def process_zip_file(batch_id, zip_path):
    """Process ZIP file"""
    try:
        batch_analyses[batch_id].update({'stage': 'Extracting files from ZIP'})
        
        extracted_files, errors = zip_handler.extract_zip(zip_path, batch_id)
        
        if errors:
            batch_analyses[batch_id].update({'status': 'failed', 'errors': errors})
            return
        
        if not extracted_files:
            batch_analyses[batch_id].update({'status': 'failed', 'errors': ['No files found in ZIP']})
            return
        
        batch_analyses[batch_id].update({
            'total_files': len(extracted_files),
            'files': {f['original_name']: {'status': 'queued', 'path': f['extracted_path']} for f in extracted_files},
            'stage': f'Queuing {len(extracted_files)} files for analysis'
        })
        
        queue_manager.add_batch(
            batch_id,
            [{'path': f['extracted_path'], 'name': f['original_name'], 'index': f['index']} for f in extracted_files],
            analyze_single_file
        )
        
        batch_analyses[batch_id].update({
            'status': 'analyzing',
            'stage': f'Analyzing files (0/{len(extracted_files)})'
        })
        
    except Exception as e:
        batch_analyses[batch_id].update({'status': 'failed', 'error': str(e)})

def analyze_single_file(file_path, analysis_id):
    """Wrapper function to analyze a single file"""
    analyzer = FileAnalyzer()
    return analyzer.analyze(file_path, analysis_id)

def run_single_analysis(analysis_id, file_path, filename):
    """Run analysis for a single file"""
    active_analyses[analysis_id].update({
        'status': 'analyzing',
        'progress': 60,
        'stage': 'Running static analysis'
    })
    
    try:
        analyzer = FileAnalyzer()
        results = analyzer.analyze(file_path, analysis_id)
        
        # Save results
        results_path = os.path.join(os.path.dirname(file_path), f"{analysis_id}_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        active_analyses[analysis_id].update({
            'status': 'completed',
            'progress': 100,
            'stage': 'Complete',
            'results': results,
            'file_path': file_path
        })
        
    except Exception as e:
        active_analyses[analysis_id].update({
            'status': 'failed',
            'error': str(e)
        })

@app.route('/api/status/<analysis_id>')
def get_status(analysis_id):
    """Get status for any analysis (single, zip, or url)"""
    # Check single file analyses
    if analysis_id in active_analyses:
        return jsonify(active_analyses[analysis_id])
    
    # Check batch analyses
    if analysis_id in batch_analyses:
        batch_status = batch_analyses[analysis_id].copy()
        
        if batch_status['status'] == 'analyzing':
            queue_status = queue_manager.get_batch_status(analysis_id)
            if queue_status:
                batch_status.update({
                    'progress': queue_status.get('progress', 0),
                    'completed_files': queue_status.get('completed', 0),
                    'failed_files': queue_status.get('failed', 0),
                    'stage': f"Analyzing files ({queue_status.get('completed', 0)}/{batch_status['total_files']})"
                })
                
                if queue_status.get('completed', 0) + queue_status.get('failed', 0) >= batch_status['total_files']:
                    batch_status['status'] = 'completed'
                    batch_status['stage'] = 'Analysis complete'
                    full_results = queue_manager.get_batch_results(analysis_id)
                    if full_results:
                        batch_status['results'] = full_results
        
        return jsonify(batch_status)
    
    return jsonify({'error': 'Analysis not found'}), 404

@app.route('/api/results/<analysis_id>')
def get_results(analysis_id):
    """Get results for any analysis"""
    # Check single file
    if analysis_id in active_analyses and 'results' in active_analyses[analysis_id]:
        return jsonify(active_analyses[analysis_id]['results'])
    
    # Check batch
    if analysis_id in batch_analyses:
        batch_results = queue_manager.get_batch_results(analysis_id)
        if batch_results:
            overall_risk = calculate_overall_risk(batch_results)
            batch_results['overall'] = overall_risk
            return jsonify(batch_results)
    
    # Try to load from file
    try:
        upload_dir = app.config['UPLOAD_FOLDER']
        url_dir = app.config['URL_DOWNLOAD_FOLDER']
        
        # Check both directories
        for directory in [upload_dir, url_dir]:
            for f in os.listdir(directory):
                if f.startswith(analysis_id) and f.endswith('_results.json'):
                    results_path = os.path.join(directory, f)
                    with open(results_path, 'r') as f:
                        results = json.load(f)
                    return jsonify(results)
    except:
        pass
    
    return jsonify({'error': 'Results not found'}), 404
@app.route('/api/sanitize/<analysis_id>', methods=['POST'])
def sanitize_file(analysis_id):
    """Sanitize a file that was already analyzed"""
    try:
        if analysis_id not in active_analyses:
            return jsonify({'error': 'Analysis not found'}), 404
        
        analysis = active_analyses[analysis_id]
        
        if analysis['status'] != 'completed':
            return jsonify({'error': 'Analysis not completed yet'}), 400
        
        if 'results' not in analysis:
            return jsonify({'error': 'No analysis results found'}), 400
        
        file_path = analysis.get('file_path')
        filename = analysis['filename']
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'Original file not found'}), 404
        
        # Check if file is a script type
        script_extensions = {'.py', '.js', '.bat', '.ps1', '.sh', '.php', '.rb', '.pl', '.vbs'}
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in script_extensions:
            return jsonify({'error': 'Sanitization only available for script files'}), 400
        
        # Read file content
        with open(file_path, 'r', errors='ignore') as f:
            file_content = f.read()
        
        if not sanitizer:
            return jsonify({'error': 'Sanitizer not available - check API key'}), 500
        
        # Perform sanitization
        sanitized_code, change_report = sanitizer.sanitize_code(
            file_path, filename, file_content, analysis['results']
        )
        
        if not sanitized_code:
            return jsonify({'error': change_report}), 500
        
        # Save sanitized file
        sanitized_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'sanitized')
        os.makedirs(sanitized_dir, exist_ok=True)
        
        # Use a clean filename for storage
        sanitized_filename = f"{analysis_id}_sanitized_{filename}"
        sanitized_path = os.path.join(sanitized_dir, sanitized_filename)
        
        with open(sanitized_path, 'w', encoding='utf-8') as f:
            f.write(sanitized_code)
        
        # Store sanitized file info
        analysis['sanitized_path'] = sanitized_path
        analysis['sanitized_available'] = True
        analysis['change_report'] = change_report
        
        return jsonify({
            'success': True,
            'message': 'File sanitized successfully',
            'analysis_id': analysis_id,
            'change_report': change_report,
            'original_filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/download/<analysis_id>/<file_type>')
def download_file(analysis_id, file_type):
    """Download original or sanitized file"""
    try:
        if analysis_id not in active_analyses:
            return jsonify({'error': 'Analysis not found'}), 404
        
        analysis = active_analyses[analysis_id]
        
        if file_type == 'original':
            file_path = analysis.get('file_path')
            filename = analysis.get('filename')
        elif file_type == 'sanitized':
            file_path = analysis.get('sanitized_path')
            # Use a clean filename without the analysis_id prefix
            original_name = analysis.get('filename', 'file')
            base = os.path.splitext(original_name)[0]
            ext = os.path.splitext(original_name)[1]
            filename = f"{base}_sanitized{ext}"
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Force download with proper headers
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
        # Add headers to prevent caching and force download
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/clean/<analysis_id>', methods=['POST'])
def clean_analysis(analysis_id):
    """Clean up resources"""
    try:
        if analysis_id in active_analyses:
            if 'sanitized_path' in active_analyses[analysis_id]:
                try:
                    os.remove(active_analyses[analysis_id]['sanitized_path'])
                except:
                    pass
            del active_analyses[analysis_id]
        
        if analysis_id in batch_analyses:
            zip_handler.cleanup_extracted(analysis_id)
            queue_manager.cleanup_batch(analysis_id)
            del batch_analyses[analysis_id]
        
        # Remove files from all directories
        for directory in [app.config['UPLOAD_FOLDER'], app.config['URL_DOWNLOAD_FOLDER']]:
            for f in os.listdir(directory):
                if f.startswith(analysis_id):
                    try:
                        os.remove(os.path.join(directory, f))
                    except:
                        pass
        
        sanitized_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'sanitized')
        for f in os.listdir(sanitized_dir):
            if f.startswith(analysis_id):
                try:
                    os.remove(os.path.join(sanitized_dir, f))
                except:
                    pass
        
        return jsonify({'status': 'cleaned'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_overall_risk(batch_results):
    """Calculate overall risk score for a batch of files"""
    if not batch_results or 'files' not in batch_results:
        return {'risk_score': 0, 'threat_level': 'UNKNOWN'}
    
    files = batch_results['files']
    if not files:
        return {'risk_score': 0, 'threat_level': 'UNKNOWN'}
    
    scores = []
    threat_levels = []
    
    for file_name, file_data in files.items():
        if file_data.get('status') == 'completed' and 'result' in file_data:
            result = file_data['result']
            scores.append(result.get('risk_score', 0))
            threat_levels.append(result.get('threat_level', 'UNKNOWN'))
    
    if not scores:
        return {'risk_score': 0, 'threat_level': 'UNKNOWN'}
    
    avg_score = sum(scores) / len(scores)
    
    threat_priority = {'CRITICAL': 5, 'SEVERE': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'SAFE': 0, 'UNKNOWN': -1}
    max_threat = max(threat_levels, key=lambda x: threat_priority.get(x, -1))
    
    return {
        'risk_score': round(avg_score),
        'threat_level': max_threat,
        'file_count': len(scores),
        'risk_distribution': {
            level: threat_levels.count(level) for level in set(threat_levels)
        }
    }

# Cleanup on shutdown
import atexit
@atexit.register
def shutdown():
    queue_manager.stop()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)