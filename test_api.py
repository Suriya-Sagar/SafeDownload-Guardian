import google.generativeai as genai
import os

# Your key
API_KEY = "AIzaSyDrwx1Qs3t89vD6Mxi693mIodh0SPy2j4g"

print(f"Testing API key: {API_KEY[:8]}...{API_KEY[-4:]}")

try:
    # Configure
    genai.configure(api_key=API_KEY)
    
    # List available models (this is a simple test)
    models = genai.list_models()
    print("✅ API Key accepted! Available models:")
    for model in models:
        print(f"  - {model.name}")
        
    # Try a simple generation
    model = genai.GenerativeModel('gemma-3-27b-it')
    response = model.generate_content("Say 'API key is working'")
    print(f"✅ Generation successful: {response.text[:50]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Try to get more details
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")