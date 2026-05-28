import docker
import os
import json
import hashlib
import subprocess
import time
import threading
from datetime import datetime
import traceback
import re
import tempfile
import base64
from dotenv import load_dotenv

load_dotenv()

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class FileAnalyzer:
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"Docker connection error: {e}")
            self.docker_client = None
        
        self.ai_model = None
        self._init_gemini()
        
        self.container = None
        self.analysis_results = {
            'static_analysis': {},
            'behavioral_analysis': {},
            'ai_analysis': {},
            'risk_score': 0,
            'threat_level': 'Unknown',
            'user_friendly_summary': {}
        }
    
    def _init_gemini(self):
        try:
            from config import Config
            import google.generativeai as genai
        
            api_key = Config.GEMINI_API_KEY
            model_name = Config.GEMINI_MODEL
        
            if not api_key:
                print("⚠️ No Gemini API key configured")
                self.ai_model = None
                return
            
            if GENAI_AVAILABLE:
                genai.configure(api_key=api_key)
                try:
                    # Use a simpler model that's definitely available
                    model_names = ['gemma-3-27b-it', 'gemini-2.5-flash', 'gemini-2.0-flash']
                    for name in model_names:
                        try:
                            self.ai_model = genai.GenerativeModel(name)
                            test_response = self.ai_model.generate_content("Say 'ready'")
                            print(f"✅ Gemini AI initialized with: {name}")
                            break
                        except:
                            continue
                except Exception as e:
                    print(f"⚠️ Gemini init failed: {e}")
                    self.ai_model = None
        except Exception as e:
            print(f"⚠️ Gemini AI initialization failed: {e}")
            self.ai_model = None
    
    def analyze(self, file_path, analysis_id):
        try:
            filename = os.path.basename(file_path)
            print(f"🚀 Analyzing {filename}")
            
            # Read the actual file content for proper analysis
            with open(file_path, 'r', errors='ignore') as f:
                file_content = f.read(50000)  # Read first 50KB
            
            # Layer 1: Static Analysis
            self.analysis_results['static_analysis'] = self._comprehensive_static_analysis(file_path, file_content)
            
            # Layer 2: Behavioral Analysis
            if self._should_analyze_behavior(file_path):
                self.analysis_results['behavioral_analysis'] = self._accurate_behavioral_analysis(file_path, analysis_id)
            else:
                self.analysis_results['behavioral_analysis'] = {
                    'note': 'Behavioral analysis not performed',
                    'suspicious_activities': [],
                    'what_happened': 'This file type cannot be executed in the sandbox.'
                }
            
            # Layer 3: AI Analysis
            if self.ai_model:
                self.analysis_results['ai_analysis'] = self._user_friendly_ai_analysis(file_content, filename)
            else:
                self.analysis_results['ai_analysis'] = {
                    'error': 'AI not available - check API key',
                    'plain_language_summary': 'AI analysis unavailable. Please check your Gemini API key configuration.',
                    'should_you_run_it': 'UNKNOWN'
                }
            
            # Calculate accurate risk score
            self.analysis_results['risk_score'] = self._calculate_accurate_risk_score()
            self.analysis_results['threat_level'] = self._get_threat_level()
            self.analysis_results['user_friendly_summary'] = self._generate_user_friendly_summary()
            
            print(f"✅ Analysis complete! Risk Score: {self.analysis_results['risk_score']}")
            return self.analysis_results
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            traceback.print_exc()
            return {
                'error': str(e),
                'risk_score': 50,
                'threat_level': 'UNKNOWN'
            }
    
    def _comprehensive_static_analysis(self, file_path, file_content):
        """Enhanced static analysis with proper file reading"""
        results = {
            'filename': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
            'file_type': 'Unknown',
            'risk_factors': [],
            'safe_indicators': [],
            'verdict': 'INCONCLUSIVE',
            'what_this_means': ''
        }
        
        try:
            # Get file type
            file_type, mime_type = self._get_file_type(file_path)
            results['file_type'] = file_type
            
            # Calculate proper hash of entire file
            with open(file_path, 'rb') as f:
                full_data = f.read()
                results['md5'] = hashlib.md5(full_data).hexdigest()
                results['sha256'] = hashlib.sha256(full_data).hexdigest()
                
                # Calculate entropy properly
                entropy = self._calculate_entropy(full_data)
                results['entropy'] = round(entropy, 2)
            
            # Convert file content to lowercase for easier matching
            content_lower = file_content.lower()
            
            risk_factors = []
            safe_indicators = []
            risk_score_contrib = 0
            
            # ===== RANSOMWARE DETECTION =====
            ransomware_indicators = {
                'keywords': ['encrypt', 'ransom', 'decrypt', 'bitcoin', 'pay', 'wallet', 'decryption'],
                'file_ops': ['.encrypted', '.locked', '.crypted'],
                'notes': ['read_me', 'ransom_note', 'how_to_decrypt']
            }
            
            found_ransomware = []
            for kw in ransomware_indicators['keywords']:
                if kw in content_lower:
                    found_ransomware.append(kw)
            
            if found_ransomware:
                risk_factors.append({
                    'type': 'RANSOMWARE',
                    'details': f'Found ransomware indicators: {", ".join(found_ransomware[:3])}',
                    'severity': 'CRITICAL',
                    'explanation': '💀 This file contains ransomware patterns. It will encrypt your files and demand payment!'
                })
                risk_score_contrib += 45
            
            # ===== KEYLOGGER DETECTION =====
            keylogger_indicators = ['keylog', 'getasynckeystate', 'keyboard', 'hook', 'capture', 'record keys']
            found_keylogger = [kw for kw in keylogger_indicators if kw in content_lower]
            if found_keylogger:
                risk_factors.append({
                    'type': 'KEYLOGGER',
                    'details': f'Found keylogger indicators',
                    'severity': 'HIGH',
                    'explanation': '⌨️ This file can record everything you type - passwords, messages, credit cards!'
                })
                risk_score_contrib += 35
            
            # ===== REVERSE SHELL / BACKDOOR =====
            backdoor_indicators = ['socket', 'connect', 'reverse shell', 'backdoor', 'c2', 'command and control']
            found_backdoor = [kw for kw in backdoor_indicators if kw in content_lower]
            if found_backdoor:
                risk_factors.append({
                    'type': 'BACKDOOR',
                    'details': f'Network backdoor detected',
                    'severity': 'CRITICAL',
                    'explanation': '🕳️ This file can give hackers remote control of your computer!'
                })
                risk_score_contrib += 40
            
            # ===== DATA EXFILTRATION =====
            exfil_indicators = ['base64', 'b64decode', 'requests.post', 'urllib', 'http://', 'https://', 'exfil']
            found_exfil = [kw for kw in exfil_indicators if kw in content_lower]
            if found_exfil:
                risk_factors.append({
                    'type': 'DATA_EXFILTRATION',
                    'details': f'Network communication detected',
                    'severity': 'HIGH',
                    'explanation': '📤 This file can send your personal data to remote servers!'
                })
                risk_score_contrib += 25
            
            # ===== PERSISTENCE =====
            persistence_indicators = ['reg add', 'schtasks', 'crontab', 'startup', 'autorun', 'run key']
            found_persistence = [kw for kw in persistence_indicators if kw in content_lower]
            if found_persistence:
                risk_factors.append({
                    'type': 'PERSISTENCE',
                    'details': f'Persistence mechanism detected',
                    'severity': 'HIGH',
                    'explanation': '🔄 This file tries to run automatically every time you start your computer!'
                })
                risk_score_contrib += 30
            
            # ===== OBFUSCATION =====
            obfuscation_indicators = ['base64', 'b64decode', 'exec(', 'eval(', 'fromCharCode']
            found_obfuscation = [kw for kw in obfuscation_indicators if kw in content_lower]
            if found_obfuscation:
                risk_factors.append({
                    'type': 'OBFUSCATION',
                    'details': f'Code obfuscation detected',
                    'severity': 'MEDIUM',
                    'explanation': '🔒 The code is hidden/encoded to avoid detection by antivirus!'
                })
                risk_score_contrib += 20
            
            # ===== PRIVILEGE ESCALATION =====
            priv_indicators = ['sudo', 'admin', 'elevate', 'uac', 'runas', 'root']
            found_priv = [kw for kw in priv_indicators if kw in content_lower]
            if found_priv:
                risk_factors.append({
                    'type': 'PRIVILEGE_ESCALATION',
                    'details': f'Admin access requested',
                    'severity': 'HIGH',
                    'explanation': '👑 This file tries to gain administrator/root privileges!'
                })
                risk_score_contrib += 25
            
            # Determine verdict based on actual risk
            if risk_score_contrib >= 60:
                results['verdict'] = 'MALICIOUS'
                results['what_this_means'] = '🔥 DANGEROUS: This file contains multiple malware indicators. DO NOT RUN!'
            elif risk_score_contrib >= 30:
                results['verdict'] = 'SUSPICIOUS'
                results['what_this_means'] = '⚠️ WARNING: This file shows suspicious behavior. Run only in isolated environment.'
            else:
                results['verdict'] = 'LIKELY_SAFE'
                results['what_this_means'] = '✅ No obvious malware indicators found. This file appears safe.'
            
            results['risk_factors'] = risk_factors
            results['safe_indicators'] = safe_indicators
            results['risk_score_contrib'] = min(risk_score_contrib, 70)
            
        except Exception as e:
            results['error'] = str(e)
            print(f"Static analysis error: {e}")
        
        return results
    
    def _accurate_behavioral_analysis(self, file_path, analysis_id):
        """Accurate behavioral analysis with proper execution"""
        results = {
            'execution_success': False,
            'suspicious_activities': [],
            'normal_activities': [],
            'what_happened': '',
            'verdict': 'NO_BEHAVIOR'
        }
        
        if not self.docker_client:
            results['error'] = 'Docker not available'
            results['what_happened'] = 'Docker is not running. Behavioral analysis skipped.'
            return results
        
        container_name = f"analysis_{analysis_id}"
        
        try:
            # Use Ubuntu for better Python support
            image = 'python:3.9-slim'
            
            try:
                self.docker_client.images.get(image)
            except:
                print(f"Pulling {image}... (this may take a moment)")
                self.docker_client.images.pull(image)
            
            # Create container with Python support
            self.container = self.docker_client.containers.run(
                image=image,
                name=container_name,
                command='tail -f /dev/null',
                detach=True,
                mem_limit='512m',
                cpu_quota=50000,
                network_mode='bridge',
                read_only=False,
                tmpfs={'/tmp': 'rw,noexec,nosuid,size=100m'},
                auto_remove=False
            )
            
            # Copy file to container
            container_path = f"/tmp/{os.path.basename(file_path)}"
            with open(file_path, 'rb') as f:
                file_data = f.read()
                self.container.put_archive('/tmp/', self._create_tar(file_data, os.path.basename(file_path)))
            
            # Check file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.py':
                try:
                    # Make the file executable
                    self.container.exec_run(f"chmod +x {container_path}")
                    
                    # Run the Python script with timeout
                    exec_result = self.container.exec_run(
                        f"timeout 15 python3 {container_path}",
                        demux=True
                    )
                    
                    # Get output
                    stdout = exec_result.output[0] if exec_result.output[0] else b''
                    stderr = exec_result.output[1] if exec_result.output[1] else b''
                    
                    output_text = (stdout + stderr).decode('utf-8', errors='ignore')
                    
                    # Analyze output for suspicious patterns
                    suspicious = []
                    
                    if 'encrypt' in output_text.lower() or 'ransom' in output_text.lower():
                        suspicious.append({
                            'activity': 'RANSOMWARE_SIMULATION',
                            'explanation': '⚠️ The file simulated ransomware behavior - file encryption and ransom note creation.'
                        })
                    
                    if 'persistence' in output_text.lower() or 'registry' in output_text.lower():
                        suspicious.append({
                            'activity': 'PERSISTENCE_ATTEMPT',
                            'explanation': '⚠️ The file tried to establish persistence (run automatically on startup).'
                        })
                    
                    if 'socket' in output_text.lower() or 'connect' in output_text.lower():
                        suspicious.append({
                            'activity': 'NETWORK_CONNECTION',
                            'explanation': '⚠️ The file attempted network communication (potential data theft).'
                        })
                    
                    # Check for file system changes
                    diff_result = self.container.diff()
                    file_changes = []
                    
                    for change in diff_result[:10]:
                        path = change['Path']
                        if path.startswith('/tmp/') and len(path) > 5:
                            file_changes.append({
                                'activity': 'FILE_CREATED',
                                'path': path,
                                'explanation': f'File was created during execution.'
                            })
                    
                    results['execution_success'] = True
                    results['suspicious_activities'] = suspicious
                    results['normal_activities'] = file_changes
                    
                    if suspicious:
                        results['verdict'] = 'MALICIOUS_BEHAVIOR'
                        results['what_happened'] = f'The file executed and showed {len(suspicious)} suspicious behaviors.'
                    else:
                        results['verdict'] = 'CLEAN_BEHAVIOR'
                        results['what_happened'] = 'The file executed but showed no suspicious behavior.'
                    
                except Exception as e:
                    results['execution_error'] = str(e)[:100]
                    results['what_happened'] = f'Execution error: {str(e)[:50]}'
            else:
                results['what_happened'] = f'File type {ext} not executable in behavioral analysis.'
            
        except Exception as e:
            results['error'] = str(e)[:100]
            results['what_happened'] = f'Analysis error: {str(e)[:50]}'
            
        finally:
            self.cleanup_container(analysis_id)
        
        return results
    
    def _user_friendly_ai_analysis(self, file_content, filename):
        """AI analysis with proper content"""
        results = {
            'vulnerabilities': [],
            'risk_assessment': '',
            'recommendations': [],
            'plain_language_summary': '',
            'should_you_run_it': '',
            'analysis_time': None
        }
        
        if not self.ai_model:
            results['plain_language_summary'] = 'AI analysis is not available. Please check your Gemini API key configuration.'
            results['should_you_run_it'] = 'UNKNOWN'
            return results
        
        try:
            start_time = time.time()
            
            # Get first 5000 chars for analysis
            content_preview = file_content[:5000]
            
            # Create prompt for AI
            prompt = f"""Analyze this Python file for security threats. Be direct and clear.

FILENAME: {filename}

CODE CONTENT (first 5000 chars):
{content_preview}

Answer these questions:
1. What type of malware is this? (Ransomware/Keylogger/Backdoor/Other/Safe)
2. What does it do? (1 sentence)
3. Should the user run it? (YES/NO/MAYBE)
4. What's the risk level? (LOW/MEDIUM/HIGH/CRITICAL)

Keep answers SHORT and CLEAR.

Answer:"""

            response = self.ai_model.generate_content(prompt)
            ai_response = response.text
            
            # Parse response
            results['plain_language_summary'] = ai_response[:500]
            
            # Determine safety
            if 'NO' in ai_response.upper() and 'RUN' in ai_response.upper():
                results['should_you_run_it'] = 'NO'
            elif 'YES' in ai_response.upper() and 'SAFE' in ai_response.upper():
                results['should_you_run_it'] = 'YES'
            else:
                results['should_you_run_it'] = 'MAYBE'
            
            # Extract risk level
            if 'CRITICAL' in ai_response.upper():
                results['risk_assessment'] = 'CRITICAL - Very dangerous!'
            elif 'HIGH' in ai_response.upper():
                results['risk_assessment'] = 'HIGH - Significant risk!'
            elif 'MEDIUM' in ai_response.upper():
                results['risk_assessment'] = 'MEDIUM - Exercise caution'
            else:
                results['risk_assessment'] = 'LOW - Probably safe'
            
            results['analysis_time'] = time.time() - start_time
            
        except Exception as e:
            results['error'] = str(e)
            results['plain_language_summary'] = f'AI analysis error: {str(e)[:100]}'
        
        return results
    
    def _calculate_accurate_risk_score(self):
        """Calculate accurate risk score"""
        score = 0
        
        # Static analysis contribution (60%)
        static = self.analysis_results.get('static_analysis', {})
        risk_factors = static.get('risk_factors', [])
        
        for factor in risk_factors:
            severity = factor.get('severity', 'MEDIUM')
            if severity == 'CRITICAL':
                score += 20
            elif severity == 'HIGH':
                score += 12
            elif severity == 'MEDIUM':
                score += 8
            else:
                score += 4
        
        score = min(score, 60)
        
        # Behavioral analysis contribution (30%)
        behavioral = self.analysis_results.get('behavioral_analysis', {})
        suspicious = behavioral.get('suspicious_activities', [])
        score += min(len(suspicious) * 15, 30)
        
        # AI analysis contribution (10%)
        ai = self.analysis_results.get('ai_analysis', {})
        if ai.get('should_you_run_it') == 'NO':
            score += 10
        elif ai.get('should_you_run_it') == 'MAYBE':
            score += 5
        
        return min(score, 100)
    
    def _get_threat_level(self):
        """Get user-friendly threat level"""
        score = self.analysis_results.get('risk_score', 0)
        
        if score < 15:
            return '✅ SAFE'
        elif score < 30:
            return '⚠️ LOW RISK'
        elif score < 50:
            return '⚠️⚠️ MEDIUM RISK'
        elif score < 75:
            return '🚨 HIGH RISK'
        else:
            return '🔥🔥 CRITICAL'
    
    def _generate_user_friendly_summary(self):
        """Generate comprehensive user-friendly summary"""
        static = self.analysis_results.get('static_analysis', {})
        behavioral = self.analysis_results.get('behavioral_analysis', {})
        ai = self.analysis_results.get('ai_analysis', {})
        score = self.analysis_results.get('risk_score', 0)
        
        # Determine verdict
        if score < 15:
            verdict_icon = "✅"
            verdict_text = "SAFE"
            verdict_color = "green"
            summary = "This file appears to be safe. No malicious patterns were detected."
        elif score < 30:
            verdict_icon = "⚠️"
            verdict_text = "LOW RISK"
            verdict_color = "yellow"
            summary = "This file has some suspicious elements but may be harmless."
        elif score < 50:
            verdict_icon = "⚠️⚠️"
            verdict_text = "MEDIUM RISK"
            verdict_color = "orange"
            summary = "This file shows concerning behavior. Do not run unless in isolated environment."
        elif score < 75:
            verdict_icon = "🚨"
            verdict_text = "HIGH RISK"
            verdict_color = "red"
            summary = "This file is likely malicious. Do NOT run on your actual computer!"
        else:
            verdict_icon = "🔥🔥"
            verdict_text = "CRITICAL"
            verdict_color = "darkred"
            summary = "This file is HIGHLY MALICIOUS! It will harm your system if executed!"
        
        return {
            'verdict_icon': verdict_icon,
            'verdict_text': verdict_text,
            'verdict_color': verdict_color,
            'one_line_summary': summary,
            'risk_factors': [f['type'] for f in static.get('risk_factors', [])],
            'what_happened': behavioral.get('what_happened', 'Analysis completed.'),
            'ai_says': ai.get('plain_language_summary', 'AI analysis not available'),
            'recommendation': self._get_recommendation(score),
            'for_normal_users': self._simple_explanation(static)
        }
    
    def _get_recommendation(self, score):
        if score < 15:
            return "✅ Safe to use normally"
        elif score < 30:
            return "⚠️ Be cautious - verify the source"
        elif score < 50:
            return "⚠️⚠️ Run only in isolated sandbox environment"
        elif score < 75:
            return "🚨 Delete or quarantine this file immediately!"
        else:
            return "🔥🔥 CRITICAL: Delete NOW and run antivirus scan!"
    
    def _simple_explanation(self, static):
        risk_factors = static.get('risk_factors', [])
        if not risk_factors:
            return "No problems found. This file looks clean."
        return f"Found {len(risk_factors)} security concerns: " + ", ".join([f['type'] for f in risk_factors[:3]])
    
    def _calculate_entropy(self, data):
        if not data:
            return 0
        entropy = 0
        for x in range(256):
            p_x = data.count(x) / len(data)
            if p_x > 0:
                import math
                entropy += -p_x * math.log2(p_x)
        return entropy
    
    def _extract_strings(self, file_path, min_length=4):
        results = {'all_strings': [], 'embedded_urls': [], 'ip_addresses': [], 'email_addresses': []}
        try:
            with open(file_path, 'rb') as f:
                data = f.read(1024 * 1024)
            strings = []
            current = []
            for b in data:
                if 32 <= b <= 126:
                    current.append(chr(b))
                else:
                    if len(current) >= min_length:
                        strings.append(''.join(current))
                    current = []
            if len(current) >= min_length:
                strings.append(''.join(current))
            results['all_strings'] = strings
        except:
            pass
        return results
    
    def _should_analyze_behavior(self, file_path):
        executable_extensions = ['.py', '.exe', '.scr', '.bat', '.ps1', '.vbs', '.js', '.sh', '.bin', '.elf']
        ext = os.path.splitext(file_path)[1].lower()
        return ext in executable_extensions
    
    def _get_file_type(self, file_path):
        if MAGIC_AVAILABLE:
            try:
                file_type = magic.from_file(file_path)
                mime_type = magic.from_file(file_path, mime=True)
                return file_type, mime_type
            except:
                pass
        try:
            result = subprocess.run(['file', '-b', file_path], capture_output=True, text=True, timeout=2)
            return result.stdout.strip(), 'application/octet-stream'
        except:
            return 'Unknown', 'application/octet-stream'
    
    def _create_tar(self, data, filename):
        import tarfile
        import io
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(data)
            tar.addfile(tarinfo, io.BytesIO(data))
        tar_stream.seek(0)
        return tar_stream.read()
    
    def cleanup_container(self, analysis_id):
        if self.container:
            try:
                self.container.stop(timeout=2)
                self.container.remove(force=True)
            except:
                pass
            self.container = None
        try:
            if self.docker_client:
                container = self.docker_client.containers.get(f"analysis_{analysis_id}")
                container.stop(timeout=2)
                container.remove(force=True)
        except:
            pass