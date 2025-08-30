#!/usr/bin/env python3
"""
LLM Server Setup Script for LM Studio
This script helps set up the LM Studio LLM server with the hermes-3-llama-3.1-8b model.
"""

import subprocess
import sys
import requests
import time
import os

def check_lm_studio_installed():
    """Check if LM Studio is installed"""
    # LM Studio is typically installed in common locations
    common_paths = [
        os.path.expanduser("~/AppData/Local/Programs/LM Studio/LM Studio.exe"),  # Windows
        os.path.expanduser("/Applications/LM Studio.app"),  # macOS
        os.path.expanduser("~/.local/share/LM Studio/LM Studio"),  # Linux
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return True
    return False

def install_lm_studio():
    """Install LM Studio"""
    print("📦 Installing LM Studio...")
    
    if sys.platform == "win32":
        print("Please download and install LM Studio from: https://lmstudio.ai")
        print("After installation, restart your terminal and run this script again.")
        return False
    elif sys.platform == "darwin":
        print("Please download and install LM Studio from: https://lmstudio.ai")
        print("After installation, restart your terminal and run this script again.")
        return False
    else:
        print("Please download and install LM Studio from: https://lmstudio.ai")
        print("After installation, restart your terminal and run this script again.")
        return False

def start_lm_studio_server():
    """Start the LM Studio server"""
    print("🚀 Starting LM Studio server...")
    print("Please follow these steps:")
    print("1. Open LM Studio application")
    print("2. Go to 'Local Server' tab")
    print("3. Click 'Start Server'")
    print("4. Make sure the server is running on http://localhost:1234")
    print("5. Load your preferred model")
    
    # Wait for user to start the server
    input("Press Enter when you have started the LM Studio server...")
    
    # Test connection
    print("⏳ Testing LM Studio server connection...")
    for i in range(10):
        try:
            test_payload = {
                "model": "test",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
                "stream": False
            }
            response = requests.post('http://localhost:1234/v1/chat/completions', 
                                   json=test_payload, timeout=5)
            if response.status_code == 200:
                print("✅ LM Studio server is running")
                return True
        except:
            time.sleep(2)
    
    print("❌ Failed to connect to LM Studio server")
    print("Please make sure:")
    print("- LM Studio is running")
    print("- Local Server is started")
    print("- Server is accessible at http://localhost:1234")
    return False

def setup_model():
    """Setup the model in LM Studio"""
    print("📥 Setting up model in LM Studio...")
    print("Please follow these steps:")
    print("1. In LM Studio, go to 'Search' tab")
    print("2. Search for 'hermes-3-llama-3.1-8b' or your preferred model")
    print("3. Download the model (this may take several minutes)")
    print("4. Go to 'Local Server' tab")
    print("5. Select your downloaded model")
    print("6. Click 'Start Server'")
    
    input("Press Enter when you have downloaded and loaded the model...")
    return True

def test_llm_integration():
    """Test the LLM integration"""
    print("🧪 Testing LLM integration...")
    
    try:
        from utils.llm_server import test_llm_connection
        
        if test_llm_connection():
            print("✅ LLM integration test successful")
            return True
        else:
            print("❌ LLM integration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM integration: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 LM Studio Setup for Audience Dropper")
    print("=" * 50)
    
    # Step 1: Check if LM Studio is installed
    print("\n1. Checking LM Studio installation...")
    if not check_lm_studio_installed():
        print("❌ LM Studio is not installed")
        install_choice = input("Would you like to install LM Studio? (y/n): ").lower()
        
        if install_choice == 'y':
            if not install_lm_studio():
                print("❌ Failed to install LM Studio. Please install manually.")
                return False
        else:
            print("❌ LM Studio is required for LLM functionality")
            return False
    else:
        print("✅ LM Studio is already installed")
    
    # Step 2: Setup model
    print("\n2. Setting up model in LM Studio...")
    if not setup_model():
        print("❌ Failed to setup model")
        return False
    
    # Step 3: Start LM Studio server
    print("\n3. Starting LM Studio server...")
    if not start_lm_studio_server():
        print("❌ Failed to start LM Studio server")
        return False
    
    # Step 4: Test integration
    print("\n4. Testing LLM integration...")
    if not test_llm_integration():
        print("❌ LLM integration test failed")
        return False
    
    print("\n🎉 LM Studio Setup Complete!")
    print("\nYou can now:")
    print("1. Run the test script: python test_llm.py")
    print("2. Start your Flask app: python app.py")
    print("3. Use the LLM-powered audience creation feature")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
