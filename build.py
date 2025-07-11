#!/usr/bin/env python3
"""
Build Script for Prosody - AI-Powered Dictation Tool

This script automates the creation of a distributable, single-file executable
using PyInstaller. It ensures a consistent and repeatable build process.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_previous_builds():
    """Remove previous build artifacts to ensure a clean build"""
    print("🧹 Cleaning previous build artifacts...")
    
    # Directories to clean
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"   Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove .spec files
    for spec_file in Path(".").glob("*.spec"):
        print(f"   Removing {spec_file}")
        spec_file.unlink()
    
    print("✅ Cleanup complete")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")
    
    # Check if main script exists
    if not os.path.exists("prosody.py"):
        print("❌ prosody.py not found in current directory")
        sys.exit(1)
    
    print("✅ Dependencies check complete")


def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable with PyInstaller...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", "prosody",
        "--onefile",
        "--windowed",
        "prosody.py"
    ]
    
    print(f"   Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        
        # Show build output location
        executable_path = Path("dist") / "prosody"
        if os.name == "nt":  # Windows
            executable_path = executable_path.with_suffix(".exe")
        
        if executable_path.exists():
            print(f"📦 Executable created: {executable_path.absolute()}")
            file_size = executable_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   Size: {file_size:.1f} MB")
        else:
            print("⚠️  Executable not found in expected location")
            
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def main():
    """Main build process"""
    print("=" * 60)
    print("🏗️  Prosody Build Script")
    print("=" * 60)
    
    # Ensure we're in the right directory
    if not os.path.exists("prosody.py"):
        print("❌ Please run this script from the prosody project root directory")
        sys.exit(1)
    
    try:
        # Step 1: Clean previous builds
        clean_previous_builds()
        print()
        
        # Step 2: Check dependencies
        check_dependencies()
        print()
        
        # Step 3: Build executable
        build_executable()
        print()
        
        print("=" * 60)
        print("🎉 Build completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Test the executable in the dist/ directory")
        print("2. Distribute the single file to users")
        print("3. Users can run it without installing Python or dependencies")
        
    except KeyboardInterrupt:
        print("\n🛑 Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()