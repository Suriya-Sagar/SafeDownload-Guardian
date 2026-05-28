import os
import tempfile
import requests
import uuid
import threading
import time
import shutil
from datetime import datetime
import hashlib
from urllib.parse import urlparse

class DownloadProtector:
    def __init__(self, upload_folder, analyzer_func, sanitizer_func=None):
        self.upload_folder = upload_folder
        self.analyzer_func = analyzer_func
        self.sanitizer_func = sanitizer_func
        self.active_downloads = {}
        self.temp_folder = os.path.join(upload_folder, 'temp_downloads')
        os.makedirs(self.temp_folder, exist_ok=True)
        
    def intercept_download(self, download_id, url, filename, headers=None):
        """
        Intercept a download before it hits disk
        Downloads to memory/temp, analyzes, and holds for user decision
        """
        try:
            # Initialize download record
            self.active_downloads[download_id] = {
                'id': download_id,
                'url': url,
                'filename': filename,
                'status': 'downloading',
                'progress': 0,
                'stage': 'Downloading file',
                'start_time': datetime.now().isoformat(),
                'temp_path': None,
                'analysis': None,
                'sanitized_path': None,
                'file_size': 0
            }
            
            # Download file to temp (stream to memory first)
            temp_path = os.path.join(self.temp_folder, f"{download_id}_{filename}")
            
            # Stream download with progress
            response = requests.get(url, headers=headers or {}, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size if available
            file_size = int(response.headers.get('content-length', 0))
            self.active_downloads[download_id]['file_size'] = file_size
            
            # Download in chunks to track progress
            downloaded = 0
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if file_size > 0:
                            progress = int((downloaded / file_size) * 100)
                            self.active_downloads[download_id]['progress'] = progress
            
            self.active_downloads[download_id].update({
                'status': 'downloaded',
                'progress': 100,
                'temp_path': temp_path,
                'stage': 'Download complete, starting analysis'
            })
            
            # Start analysis in background
            thread = threading.Thread(
                target=self._analyze_download,
                args=(download_id, temp_path, filename)
            )
            thread.daemon = True
            thread.start()
            
            return {
                'success': True,
                'download_id': download_id,
                'message': 'Download intercepted, analysis started'
            }
            
        except Exception as e:
            self.active_downloads[download_id]['status'] = 'failed'
            self.active_downloads[download_id]['error'] = str(e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_download(self, download_id, file_path, filename):
        """Analyze the downloaded file"""
        try:
            self.active_downloads[download_id].update({
                'status': 'analyzing',
                'stage': 'Running security analysis'
            })
            
            # Generate unique analysis ID
            analysis_id = str(uuid.uuid4())
            
            # Run analyzer (YOUR EXISTING ANALYZER)
            results = self.analyzer_func(file_path, analysis_id)
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            self.active_downloads[download_id].update({
                'status': 'analyzed',
                'analysis': results,
                'file_hash': file_hash,
                'stage': 'Analysis complete'
            })
            
            # If sanitizer is available and file is script, create sanitized version
            if self.sanitizer_func and self._is_script_file(filename):
                self._create_sanitized_version(download_id, file_path, filename, results)
            
        except Exception as e:
            self.active_downloads[download_id].update({
                'status': 'failed',
                'error': str(e)
            })
    
    def _create_sanitized_version(self, download_id, file_path, filename, analysis_results):
        """Create sanitized version of the file"""
        try:
            self.active_downloads[download_id]['stage'] = 'Creating sanitized version'
            
            # Read file content
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
            
            # Run sanitizer
            sanitized_code, report = self.sanitizer_func(
                file_path, filename, content, analysis_results
            )
            
            if sanitized_code:
                sanitized_path = os.path.join(
                    self.temp_folder, 
                    f"{download_id}_sanitized_{filename}"
                )
                
                with open(sanitized_path, 'w', encoding='utf-8') as f:
                    f.write(sanitized_code)
                
                self.active_downloads[download_id].update({
                    'sanitized_path': sanitized_path,
                    'sanitized_available': True,
                    'change_report': report
                })
            else:
                self.active_downloads[download_id]['sanitized_available'] = False
                
        except Exception as e:
            print(f"Sanitization error: {e}")
            self.active_downloads[download_id]['sanitized_available'] = False
    
    def _is_script_file(self, filename):
        """Check if file is a script that can be sanitized"""
        script_extensions = {'.py', '.js', '.bat', '.ps1', '.sh', '.php', '.rb', '.pl', '.vbs'}
        ext = os.path.splitext(filename)[1].lower()
        return ext in script_extensions
    
    def get_download_status(self, download_id):
        """Get status of a download"""
        if download_id in self.active_downloads:
            return self.active_downloads[download_id]
        return None
    
    def user_decision(self, download_id, decision):
        """
        Handle user decision: 'block', 'original', or 'sanitized'
        """
        if download_id not in self.active_downloads:
            return {'error': 'Download not found'}
        
        download = self.active_downloads[download_id]
        
        if decision == 'block':
            # Delete temp file and remove record
            self._cleanup_download(download_id)
            return {
                'decision': 'block',
                'message': 'Download blocked'
            }
            
        elif decision == 'original':
            # Return original file path for download
            if download.get('temp_path') and os.path.exists(download['temp_path']):
                return {
                    'decision': 'original',
                    'file_path': download['temp_path'],
                    'filename': download['filename'],
                    'message': 'Original file ready'
                }
            else:
                return {'error': 'Original file not found'}
                
        elif decision == 'sanitized':
            # Return sanitized file path
            if download.get('sanitized_path') and os.path.exists(download['sanitized_path']):
                return {
                    'decision': 'sanitized',
                    'file_path': download['sanitized_path'],
                    'filename': f"sanitized_{download['filename']}",
                    'message': 'Sanitized file ready'
                }
            else:
                return {'error': 'Sanitized file not available'}
        
        return {'error': 'Invalid decision'}
    
    def _cleanup_download(self, download_id):
        """Clean up temporary files"""
        if download_id in self.active_downloads:
            download = self.active_downloads[download_id]
            
            # Remove temp file
            if download.get('temp_path') and os.path.exists(download['temp_path']):
                try:
                    os.remove(download['temp_path'])
                except:
                    pass
            
            # Remove sanitized file
            if download.get('sanitized_path') and os.path.exists(download['sanitized_path']):
                try:
                    os.remove(download['sanitized_path'])
                except:
                    pass
            
            # Remove from active downloads after 5 minutes
            def delayed_cleanup():
                time.sleep(300)  # 5 minutes
                if download_id in self.active_downloads:
                    del self.active_downloads[download_id]
            
            threading.Thread(target=delayed_cleanup).start()