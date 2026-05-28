from analyzer import FileAnalyzer
import os
import json

def test_analysis():
    analyzer = FileAnalyzer()
    test_file = r"c:\Users\sivag\OneDrive\Attachments\Desktop\file-sandbox\test_behavioral.py"
    
    if not os.path.exists(test_file):
        print(f"Error: {test_file} not found")
        return
        
    print(f"Starting analysis of {test_file}...")
    results = analyzer.analyze(test_file, "test_verification_01")
    
    print("\n" + "="*30)
    print("BEHAVIORAL ANALYSIS RESULTS:")
    print("="*30)
    behavioral = results.get('behavioral_analysis', {})
    
    print(f"Suspicious Activities: {len(behavioral.get('suspicious_activity', []))}")
    for act in behavioral.get('suspicious_activity', []):
        print(f" - {act}")
        
    print(f"\nNetwork Attempts: {len(behavioral.get('network_attempts', []))}")
    for net in behavioral.get('network_attempts', []):
        print(f" - {net}")
        
    print(f"\nFile Operations: {len(behavioral.get('file_operations', []))}")
    # print only top 5 to avoid noise if any remains
    for op in behavioral.get('file_operations', [])[:10]:
        print(f" - {op}")
        
    print("\n" + "="*30)
    print("AI ANALYSIS SUMMARY:")
    print("="*30)
    ai = results.get('ai_analysis', {})
    for vuln in ai.get('vulnerabilities', []):
        print(f" - {vuln.get('severity')}: {vuln.get('description')}")

if __name__ == "__main__":
    test_analysis()
