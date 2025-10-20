#!/usr/bin/env python3
"""
Setup script for Visual Agent
Installs dependencies and sets up the environment
"""

import os
import sys
import subprocess
import json


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ["output", "logs", "temp"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")


def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    try:
        from visual_agent import VisualAgent
        agent = VisualAgent()

        # Test basic functionality
        test_text = "Start -> Process -> End"
        html = agent.generate_html(test_text, "flowchart")

        if html and "<svg" in html:
            print("✅ Installation test passed")
            return True
        else:
            print("❌ Installation test failed - no SVG generated")
            return False

    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False


def create_docker_setup():
    """Create Docker setup files if they don't exist"""
    if not os.path.exists("docker-compose.yml"):
        print("📝 Docker Compose file already exists")
    else:
        print("📝 Docker Compose file created")


def main():
    """Main setup function"""
    print("🚀 Visual Agent Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return 1

    # Install dependencies
    if not install_dependencies():
        return 1

    # Create directories
    create_directories()

    # Test installation
    if not test_installation():
        return 1

    # Create Docker setup
    create_docker_setup()

    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run tests: python test_examples.py")
    print("2. Start with Docker: docker-compose up -d")
    print("3. Or run directly: python visual_agent.py")

    return 0


if __name__ == "__main__":
    exit(main())
