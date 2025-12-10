#!/usr/bin/env python3
"""
Setup script for PawScript - Dog Prescription Reader
"""

import os
import sys
import subprocess
import platform

def check_dependencies():
    """Check if required system dependencies are installed"""
    system = platform.system().lower()
    
    print("🔍 Checking system dependencies...")
    
    # Check Tesseract
    try:
        subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
        print("✅ Tesseract OCR is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract OCR not found. Please install:")
        if system == 'darwin':  # macOS
            print("   brew install tesseract")
        elif system == 'linux':
            print("   sudo apt-get install tesseract-ocr")
        elif system == 'windows':
            print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    # Check Poppler for PDF processing (optional but recommended)
    try:
        if system in ['darwin', 'linux']:
            subprocess.run(['pdftoppm', '-v'], capture_output=True, check=True)
            print("✅ Poppler utilities are installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Poppler not found. PDF processing may be limited.")
        if system == 'darwin':
            print("   Consider: brew install poppler")
        elif system == 'linux':
            print("   Consider: sudo apt-get install poppler-utils")
    
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists('venv'):
        print("🐍 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    # Determine activation script
    if platform.system() == 'Windows':
        activate_script = 'venv\\Scripts\\activate'
        pip_executable = 'venv\\Scripts\\pip'
    else:
        activate_script = 'venv/bin/activate'
        pip_executable = 'venv/bin/pip'
    
    print("📦 Installing Python dependencies...")
    subprocess.run([pip_executable, 'install', '-r', 'requirements.txt'], check=True)
    
    return activate_script

def create_directories():
    """Create necessary directories"""
    directories = [
        'static/uploads',
        'static/css',
        'static/js',
        'static/images',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def main():
    print("🚀 Setting up PawScript - Dog Prescription Reader")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and run setup again.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create virtual environment and install packages
    try:
        activate_script = create_virtual_environment()
        print("✅ Virtual environment setup complete")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup virtual environment: {e}")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print(f"1. Activate virtual environment:")
    if platform.system() == 'Windows':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Run the application:")
    print("   python app.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\nFor support, contact: help@pawscript.com")

if __name__ == '__main__':
    main()