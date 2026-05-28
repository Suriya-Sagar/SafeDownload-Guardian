import base64
import os
import sys
import time
import urllib.request
import requests

def calculate_checksum(filename):
    """Calculates the SHA-256 checksum of a file."""
    try:
        with open(filename, "rb") as f:
            content = f.read()
            import hashlib
            checksum = hashlib.sha256(content).hexdigest()
            return checksum
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error calculating checksum: {e}")
        return None

def simulate_encryption(filename):
    """Simulates encrypting a file by changing its contents."""
    try:
        with open(filename, "rb") as f:
            content = f.read()
        encrypted_content = base64.b64encode(content)
        with open(filename + ".enc", "wb") as f:
            f.write(encrypted_content)
        os.remove(filename)
        print(f"File '{filename}' encrypted and renamed to '{filename}.enc'")
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
    except Exception as e:
        print(f"Error encrypting file: {e}")

def simulate_decryption(filename):
    """Simulates decrypting a file by reversing the encryption."""
    try:
        with open(filename, "rb") as f:
            encrypted_content = f.read()
        decrypted_content = base64.b64decode(encrypted_content)
        with open(filename[:-4], "wb") as f:
            f.write(decrypted_content)
        os.remove(filename)
        print(f"File '{filename}' decrypted and renamed to '{filename[:-4]}'")
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
    except Exception as e:
        print(f"Error decrypting file: {e}")

def keylogger():
    """Simulates keylogging by printing keystrokes."""
    # REMOVED: import pynput
    # REASON: Keylogging functionality
    # REMOVED: from pynput.keyboard import Key, Listener
    # REASON: Keylogging functionality
    # REMOVED: def on_press(key):
    # REASON: Keylogging functionality
    # REMOVED:     try:
    # REASON: Keylogging functionality
    # REMOVED:         print('alphanumeric key {0} pressed'.format(key.char))
    # REASON: Keylogging functionality
    # REMOVED:     except AttributeError:
    # REASON: Keylogging functionality
    # REMOVED:         print('special key {0} pressed'.format(key))
    # REASON: Keylogging functionality
    # REMOVED: def on_release(key):
    # REASON: Keylogging functionality
    # REMOVED:     if key == Key.esc:
    # REASON: Keylogging functionality
    # REMOVED:         return False
    # REASON: Keylogging functionality
    # REMOVED: with Listener(on_press=on_press, on_release=on_release) as listener:
    # REASON: Keylogging functionality
    # REMOVED:     listener.join()
    # REASON: Keylogging functionality
    print("Keylogging simulation disabled.")

def network_communication():
    """Simulates network communication."""
    # REMOVED: import socket
    # REASON: Network communication - potential backdoor
    # REMOVED: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # REASON: Network communication - potential backdoor
    # REMOVED: s.connect(('127.0.0.1', 12345))
    # REASON: Network communication - potential backdoor
    # REMOVED: s.send(b'Hello, server!')
    # REASON: Network communication - potential backdoor
    # REMOVED: data = s.recv(1024)
    # REASON: Network communication - potential backdoor
    # REMOVED: print('Received', repr(data))
    # REASON: Network communication - potential backdoor
    # REMOVED: s.close()
    # REASON: Network communication - potential backdoor
    print("Network communication simulation disabled.")

def persistence():
    """Simulates persistence by adding a script to startup."""
    # REMOVED: import winreg
    # REASON: Persistence mechanism
    # REMOVED: key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
    # REASON: Persistence mechanism
    # REMOVED: winreg.SetValueEx(key, "RansomwareSimulator", 0, winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
    # REASON: Persistence mechanism
    # REMOVED: winreg.CloseKey(key)
    # REASON: Persistence mechanism
    print("Persistence simulation disabled.")

def obfuscated_code():
    """Simulates obfuscated code execution."""
    # REMOVED: encoded_string = "aGVsbG8gd29ybGQ="
    # REASON: Obfuscated code - base64 encoded string
    # REMOVED: decoded_string = base64.b64decode(encoded_string).decode()
    # REASON: Obfuscated code - base64 decoding
    # REMOVED: exec(decoded_string)
    # REASON: Obfuscated code - dynamic execution of decoded string
    print("Obfuscated code simulation disabled.")

def main():
    """Main function to simulate ransomware behavior."""
    print("Ransomware Simulator")

    target_file = input("Enter the name of the file to 'encrypt': ")

    calculate_checksum(target_file)

    simulate_encryption(target_file)

    # REMOVED: keylogger()
    # REASON: Keylogging functionality

    # REMOVED: network_communication()
    # REASON: Network communication - potential backdoor

    # REMOVED: persistence()
    # REASON: Persistence mechanism

    # REMOVED: obfuscated_code()
    # REASON: Obfuscated code execution

    simulate_decryption(target_file + ".enc")

if __name__ == "__main__":
    main()