import google.generativeai as genai
import os
import re
from datetime import datetime
import traceback

class CodeSanitizer:
    def __init__(self, api_key, model_name='gemma-3-27b-it'):
        """Initialize the code sanitizer with Gemini AI"""
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self._init_model()
        
    def _init_model(self):
        """Initialize Gemini model"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            print(f"✅ Sanitizer model initialized: {self.model_name}")
        except Exception as e:
            print(f"❌ Sanitizer initialization failed: {e}")
            self.model = None
    
    def get_comment_syntax(self, file_ext):
        """Get comment syntax for different file types"""
        comment_syntax = {
            '.py': {'single': '#', 'example': '#'},
            '.js': {'single': '//', 'example': '//'},
            '.bat': {'single': 'REM', 'example': 'REM'},
            '.ps1': {'single': '#', 'example': '#'},
            '.sh': {'single': '#', 'example': '#'},
            '.php': {'single': '//', 'example': '//'},
            '.rb': {'single': '#', 'example': '#'},
            '.pl': {'single': '#', 'example': '#'},
            '.vbs': {'single': "'", 'example': "'"},
            '.txt': {'single': '#', 'example': '#'}
        }
        return comment_syntax.get(file_ext, {'single': '#', 'example': '#'})
    
    def sanitize_code(self, file_path, original_filename, file_content, analysis_results):
        """
        Sanitize malicious code by REMOVING vulnerable lines
        Preserves ALL legitimate functions and code structure
        """
        if not self.model:
            return None, "Sanitizer model not available - check API key"
        
        try:
            # Extract file extension
            file_ext = os.path.splitext(original_filename)[1].lower()
            
            # Get comment syntax
            comment_syntax = self.get_comment_syntax(file_ext)
            comment_char = comment_syntax['single']
            
            # First try: Regex-based removal (fast and reliable)
            sanitized_code, removed_lines = self._regex_remove_malicious(file_content, file_ext)
            
            # If regex made changes, use it
            if removed_lines > 0:
                print(f"✅ Regex removal removed {removed_lines} malicious lines")
            else:
                # Second try: AI-based removal
                print("⚠️ No regex matches, trying AI removal...")
                sanitized_code = self._ai_remove_malicious(file_content, file_ext, original_filename, comment_char)
                
                # Verify AI made changes
                if sanitized_code == file_content:
                    print("❌ AI removal failed to make changes")
                    return file_content, {
                        'filename': original_filename,
                        'sanitized_at': datetime.now().isoformat(),
                        'warning': 'Could not sanitize - no malicious patterns matched',
                        'vulnerabilities_removed': []
                    }
            
            # Generate change report
            change_report = self._generate_detailed_change_report(
                original_filename, removed_lines
            )
            
            print(f"✅ Sanitization successful for {original_filename}")
            return sanitized_code, change_report
            
        except Exception as e:
            print(f"❌ Sanitization error: {e}")
            traceback.print_exc()
            return file_content, {
                'filename': original_filename,
                'sanitized_at': datetime.now().isoformat(),
                'error': f"Sanitization failed: {str(e)}",
                'vulnerabilities_removed': []
            }
    
    def _regex_remove_malicious(self, content, file_ext):
        """Remove malicious lines completely - preserves code structure"""
        lines = content.split('\n')
        sanitized_lines = []
        removed_count = 0
        skip_next_line = False
        
        # Patterns that indicate malicious lines to remove
        malicious_patterns = [
            # Network requests
            (r'fetch\s*\(', 'fetch() network request'),
            (r'navigator\.sendBeacon\s*\(', 'sendBeacon data exfiltration'),
            (r'\.sendBeacon\s*\(', 'sendBeacon data exfiltration'),
            (r'urlopen\s*\(', 'URL open request'),
            (r'requests\.(get|post|put|delete)\s*\(', 'HTTP request'),
            (r'urllib\.request\.urlopen\s*\(', 'URL open request'),
            (r'XMLHttpRequest\s*\(\s*\)', 'XHR network request'),
            (r'\.open\s*\(\s*["\']POST["\']', 'XHR POST request'),
            (r'Invoke-WebRequest', 'PowerShell web request'),
            (r'Invoke-RestMethod', 'PowerShell REST request'),
            (r'wget\s+https?://', 'wget download'),
            (r'curl\s+https?://', 'curl download'),
            (r'new\s+Image\(\)\.src\s*=', 'image beacon'),
            
            # Code execution
            (r'eval\s*\(\s*["\']', 'eval() code execution'),
            (r'exec\s*\(\s*["\']', 'exec() code execution'),
            (r'base64\.b64decode\s*\(', 'base64 decode'),
            (r'from base64 import', 'base64 import'),
            (r'import base64', 'base64 import'),
            (r'\[System\.Convert\]::FromBase64String', 'PowerShell base64 decode'),
            (r'atob\s*\(', 'JavaScript base64 decode'),
            (r'btoa\s*\(', 'JavaScript base64 encode'),
            
            # Malicious scripts
            (r'document\.head\.appendChild', 'DOM manipulation'),
            (r'createElement\s*\(\s*["\']script["\']', 'script injection'),
            (r'\.src\s*=\s*["\']https?://', 'external script load'),
            
            # Keyloggers
            (r'addEventListener\s*\(\s*["\']keypress["\']', 'keypress listener'),
            (r'addEventListener\s*\(\s*["\']keydown["\']', 'keydown listener'),
            (r'addEventListener\s*\(\s*["\']keyup["\']', 'keyup listener'),
            
            # Malicious URLs and patterns
            (r'malicious-', 'malicious URL pattern'),
            (r'evil\.com', 'malicious domain'),
            (r'crypto-miner', 'cryptominer'),
            (r'coinhive', 'cryptominer'),
            (r'fingerprint-collector', 'fingerprint collection'),
            (r'data-exfiltrator', 'data exfiltration'),
            (r'form-stealer', 'form data theft'),
            
            # Malicious function calls
            (r'stealBrowserData\s*\(', 'data theft function'),
            (r'startMiner\s*\(', 'cryptominer function'),
            (r'exfiltrateData\s*\(', 'data exfiltration function'),
            (r'collectUserData\s*\(', 'data collection function'),
            (r'mineInBackground\s*\(', 'cryptomining function'),
            (r'execute_payload\s*\(', 'payload execution'),
            (r'steal_system_info\s*\(', 'system info theft'),
            (r'keylog_simulation\s*\(', 'keylogger simulation'),
            
            # Variable assignments with malicious URLs
            (r'const\s+C2_SERVER\s*=', 'C2 server variable'),
            (r'let\s+C2_SERVER\s*=', 'C2 server variable'),
            (r'var\s+C2_SERVER\s*=', 'C2 server variable'),
            
            # PowerShell specific
            (r'Start-Process.*-WindowStyle Hidden', 'hidden process start'),
            (r'powershell.*-Command', 'PowerShell command execution'),
            (r'cmd\.exe.*\/c', 'cmd execution'),
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()
            is_malicious = False
            
            # Skip empty lines
            if not line_stripped:
                sanitized_lines.append(line)
                i += 1
                continue
            
            # Check each pattern
            for pattern, description in malicious_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_malicious = True
                    removed_count += 1
                    print(f"Removing malicious line: {line_stripped[:80]}...")
                    break
            
            if is_malicious:
                # Skip this line entirely (don't add to output)
                i += 1
                continue
            
            # Keep safe lines
            sanitized_lines.append(line)
            i += 1
        
        # Clean up: remove empty lines that were created (optional)
        result_lines = []
        for line in sanitized_lines:
            if line.strip() or (result_lines and result_lines[-1].strip()):
                result_lines.append(line)
        
        return '\n'.join(result_lines), removed_count
    
    def _ai_remove_malicious(self, content, file_ext, filename, comment_char):
        """Fallback AI-based removal"""
        
        lang_names = {
            '.py': 'Python', '.js': 'JavaScript', '.bat': 'Batch', '.ps1': 'PowerShell',
            '.sh': 'Shell', '.php': 'PHP', '.rb': 'Ruby', '.pl': 'Perl', '.vbs': 'VBScript'
        }
        language = lang_names.get(file_ext, 'Script')
        
        prompt = f"""Remove ALL malicious lines from this {language} code. Keep the code structure intact.

CRITICAL RULES:
1. REMOVE entire lines containing malicious code
2. DO NOT modify safe lines
3. KEEP all function definitions, class definitions, and legitimate logic
4. The code must remain syntactically correct after removal

Remove lines containing:
- fetch(, sendBeacon(, eval(, exec(, base64, XMLHttpRequest
- addEventListener('keypress', addEventListener('keydown'
- document.head.appendChild, createElement('script')
- malicious, evil, crypto-miner, coinhive
- stealBrowserData, startMiner, exfiltrateData, collectUserData
- C2_SERVER, Image().src with external URLs

Original code:


Return ONLY the cleaned code with malicious lines removed.

CLEANED CODE:"""
        
        try:
            generation_config = {'temperature': 0.0, 'max_output_tokens': 8192}
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            if response and response.text:
                sanitized = response.text
                # Remove markdown
                sanitized = re.sub(r'```\w*\n', '', sanitized)
                sanitized = re.sub(r'```', '', sanitized)
                return sanitized.strip()
        except Exception as e:
            print(f"AI removal failed: {e}")
        
        return content
    
    def _generate_detailed_change_report(self, filename, removed_lines):
        """Generate a detailed change report for UI display"""
        
        report = {
            'filename': filename,
            'sanitized_at': datetime.now().isoformat(),
            'total_vulnerabilities': removed_lines,
            'vulnerabilities_removed': [],
            'summary': '',
            'changes_made': []
        }
        
        if removed_lines == 0:
            report['summary'] = "⚠️ No malicious patterns were detected in this file."
        else:
            report['summary'] = f"🛡️ Removed {removed_lines} malicious line(s) from the file. The code is now safe to use."
            report['changes_made'] = [{
                'action': 'Line removed',
                'reason': 'Malicious code pattern detected and removed'
            }]
        
        return report


def sanitize_file_content(api_key, file_path, filename, content, analysis_results):
    """Convenience function to sanitize a file"""
    sanitizer = CodeSanitizer(api_key)
    return sanitizer.sanitize_code(file_path, filename, content, analysis_results)