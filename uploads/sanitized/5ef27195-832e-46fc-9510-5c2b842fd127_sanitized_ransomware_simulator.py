#!/usr/bin/env python3
"""
RANSOMWARE SIMULATOR - FOR SECURITY TESTING ONLY
DO NOT RUN ON ACTUAL SYSTEMS
"""

import os
import sys
import platform
from datetime import datetime

class RansomwareSimulator:
    def __init__(self):
        self.files_encrypted = 0
        self.ransom_note = """
        ========================================
        🔒 YOUR FILES HAVE BEEN ENCRYPTED 🔒
        ========================================

        This is a SIMULATION for security testing.

        In a real attack:
        - All your documents would be encrypted
        - You would need to pay a ransom
        - Your data would be at risk

        This is a TEST file. No actual encryption occurred.

        ========================================
        SECURITY TEST COMPLETE
        ========================================
        """

    def simulate_encryption(self):
        print("[SIMULATION] Starting ransomware simulation...")
        print("[SIMULATION] Looking for documents to encrypt...")

        # Simulate file search
        test_paths = [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
            "/tmp/test_files"
        ]

        for path in test_paths:
            if os.path.exists(path):
                print(f"[SIMULATION] Found target directory: {path}")
                for root, dirs, files in os.walk(path):
                    for file in files[:10]:  # Limit for simulation
                        if file.endswith(('.doc', '.pdf', '.jpg', '.txt')):
                            print(f"[SIMULATION] Would encrypt: {os.path.join(root, file)}")
                            self.files_encrypted += 1

        print(f"[SIMULATION] {self.files_encrypted} files would be encrypted")

    def simulate_ransom_note(self):
        print("[SIMULATION] Creating ransom note...")
        ransom_path = os.path.expanduser("~/Desktop/READ_ME_FOR_DECRYPT.txt")
        print(f"[SIMULATION] Ransom note would be placed at: {ransom_path}")
        print(self.ransom_note)

    def simulate_persistence(self):
        print("[SIMULATION] Establishing persistence...")

        if platform.system() == "Windows":
            print("[SIMULATION] Would add registry key: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
            print("[SIMULATION] Would create scheduled task for persistence")
        else:
            print("[SIMULATION] Would add to crontab: @reboot /path/to/malware")
            print("[SIMULATION] Would create systemd service")

    def run(self):
        print("="*60)
        print("RANSOMWARE SIMULATION - SECURITY TEST")
        print("="*60)
        print("WARNING: This is a simulation. No actual encryption occurs.")
        print("="*60)

        self.simulate_encryption()
        self.simulate_ransom_note()
        self.simulate_persistence()

        print("\n[SIMULATION] Complete - System would be compromised")
        print("[SIMULATION] Your sandbox should detect:")
        print("  - File encryption attempts")
        print("  - Ransom note creation")
        print("  - Persistence mechanisms")
        print("  - High-risk behavior")

        return {
            "threat_level": "CRITICAL",
            "type": "Ransomware Simulator",
            "behaviors": ["File Encryption", "Ransom Note", "Persistence", "System Modification"]
        }

if __name__ == "__main__":
    simulator = RansomwareSimulator()
    simulator.run()