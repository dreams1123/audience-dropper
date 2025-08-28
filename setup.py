#!/usr/bin/env python3
"""
Setup script for Audience Dropper
This script helps you get started with the project.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Audience Dropper Setup")
    print("=" * 50)
    
    # Check if Python is installed
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file from template...")
        if os.path.exists('env.example'):
            with open('env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ .env file created successfully!")
        else:
            print("❌ env.example file not found")
            return
    else:
        print("✅ .env file already exists")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return
    
    # Initialize database
    if not run_command("python init_db.py", "Initializing database"):
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the application: python app.py")
    print("2. Open your browser and go to: http://localhost:5000")
    print("3. Sign in with: admin@audiencedropper.com / admin123")
    print("4. Or request access as a new user")
    print("\n🔐 Login Credentials:")
    print("   Email: admin@audiencedropper.com")
    print("   Password: admin123")
    
    print("\n💡 Tips:")
    print("- The application uses your MongoDB Atlas connection")
    print("- All data is stored securely in the cloud")
    print("- You can create new users through the 'Request Access' feature")
    print("- The clean white/light design makes the interface stand out")

if __name__ == '__main__':
    main()
