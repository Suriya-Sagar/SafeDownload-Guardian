import zipfile
import os
import shutil
import tempfile
import uuid
from datetime import datetime
import threading
import time

class ZIPHandler:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.extract_folder = os.path.join(upload_folder, 'extracted')
        os.makedirs(self.extract_folder, exist_ok=True)
        
    def extract_zip(self, zip_path, analysis_id):
        """
        Extract ZIP file safely and return list of extracted files
        """
        extracted_files = []
        errors = []
        
        # Create unique extraction directory for this analysis
        extract_dir = os.path.join(self.extract_folder, analysis_id)
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            # Open ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for ZIP bomb (too many files or too large)
                total_size = sum(file.file_size for file in zip_ref.filelist)
                file_count = len(zip_ref.filelist)
                
                # Safety limits
                MAX_FILES = 100  # Max 100 files per ZIP
                MAX_SIZE = 500 * 1024 * 1024  # 500MB total extracted size
                
                if file_count > MAX_FILES:
                    errors.append(f"ZIP contains too many files ({file_count} > {MAX_FILES})")
                    return extracted_files, errors
                
                if total_size > MAX_SIZE:
                    errors.append(f"ZIP too large after extraction ({total_size/(1024*1024):.1f}MB > {MAX_SIZE/(1024*1024)}MB)")
                    return extracted_files, errors
                
                # Extract all files safely
                for file_info in zip_ref.filelist:
                    # Prevent directory traversal attacks
                    filename = os.path.basename(file_info.filename)
                    if not filename:  # Skip directories
                        continue
                        
                    # Extract file
                    source = zip_ref.open(file_info)
                    target_path = os.path.join(extract_dir, f"{len(extracted_files)}_{filename}")
                    
                    with open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    extracted_files.append({
                        'original_name': file_info.filename,
                        'extracted_path': target_path,
                        'size': file_info.file_size,
                        'index': len(extracted_files)
                    })
                    
        except zipfile.BadZipFile:
            errors.append("Invalid ZIP file")
        except Exception as e:
            errors.append(f"Extraction error: {str(e)}")
            
        return extracted_files, errors
    
    def cleanup_extracted(self, analysis_id):
        """Remove extracted files after analysis"""
        extract_dir = os.path.join(self.extract_folder, analysis_id)
        try:
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
        except:
            pass