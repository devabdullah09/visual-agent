#!/usr/bin/env python3
"""
Local Installation Script for Visual Agent
Sets up the visual agent without Docker
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(
            f"   Current version: {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def create_directories():
    """Create necessary directories"""
    directories = ["output", "logs", "temp", "examples"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")


def create_startup_scripts():
    """Create startup scripts for different platforms"""
    if platform.system() == "Windows":
        # Windows batch file
        batch_content = """@echo off
echo Starting Visual Agent Server...
python run_local.py
pause
"""
        with open("start_visual_agent.bat", "w") as f:
            f.write(batch_content)
        print("📝 Created start_visual_agent.bat")

        # Windows PowerShell script
        ps_content = """# Visual Agent Startup Script
Write-Host "Starting Visual Agent Server..." -ForegroundColor Green
python run_local.py
"""
        with open("start_visual_agent.ps1", "w") as f:
            f.write(ps_content)
        print("📝 Created start_visual_agent.ps1")

    else:
        # Unix shell script
        shell_content = """#!/bin/bash
echo "Starting Visual Agent Server..."
python3 run_local.py
"""
        with open("start_visual_agent.sh", "w") as f:
            f.write(shell_content)
        os.chmod("start_visual_agent.sh", 0o755)
        print("📝 Created start_visual_agent.sh")


def create_example_files():
    """Create example input files"""
    examples = {
        "flowchart_example.txt": """Start
User visits website
Check if user is logged in?
Yes: Show dashboard
No: Show login page
User enters credentials
Validate credentials?
Yes: Redirect to dashboard
No: Show error message
End""",

        "diagram_example.txt": """Frontend Application connects to API Gateway
API Gateway routes to Authentication Service
API Gateway routes to Product Service
Authentication Service queries User Database
Product Service queries Product Database
API Gateway sends response to Frontend""",

        "chart_example.txt": """Q1 2023: 45000
Q2 2023: 52000
Q3 2023: 48000
Q4 2023: 61000
Q1 2024: 58000
Q2 2024: 67000
Q3 2024: 72000
Q4 2024: 85000"""
    }

    for filename, content in examples.items():
        with open(f"examples/{filename}", "w") as f:
            f.write(content)
        print(f"📄 Created example: {filename}")


def create_config_file():
    """Create configuration file"""
    config = {
        "server": {
            "port": 8080,
            "host": "localhost",
            "auto_open_browser": True
        },
        "visual_agent": {
            "default_type": "auto",
            "enable_secret_redaction": True,
            "max_text_length": 10000
        },
        "output": {
            "directory": "output",
            "format": "html",
            "include_timestamp": True
        }
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("⚙️  Created config.json")


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


def create_readme_local():
    """Create local README"""
    readme_content = """# Visual Agent - Local Installation

## Quick Start

### Option 1: Run the Server
```bash
python run_local.py
```
Then open http://localhost:8080 in your browser.

### Option 2: Use Startup Scripts
- **Windows**: Double-click `start_visual_agent.bat` or run `start_visual_agent.ps1`
- **Mac/Linux**: Run `./start_visual_agent.sh`

### Option 3: Command Line API
```bash
# Generate flowchart
python -c "from visual_agent import VisualAgent; agent = VisualAgent(); print(agent.generate_html('Start -> Process -> End', 'flowchart'))"

# Generate diagram
python -c "from visual_agent import VisualAgent; agent = VisualAgent(); print(agent.generate_html('A connects to B', 'diagram'))"

# Generate chart
python -c "from visual_agent import VisualAgent; agent = VisualAgent(); print(agent.generate_html('Q1: 1000\\nQ2: 2000', 'chart'))"
```

## Features

- **Web Interface**: Interactive demo at http://localhost:8080
- **API Endpoint**: POST to http://localhost:8080/api/generate
- **Example Files**: Check the `examples/` directory
- **Configuration**: Modify `config.json` for custom settings

## API Usage

Send POST request to `http://localhost:8080/api/generate`:

```json
{
  "text": "Your text here",
  "visual_type": "auto"
}
```

Response:
```json
{
  "html_output": "<!DOCTYPE html>...",
  "visual_type": "flowchart",
  "text_length": 25
}
```

## Examples

Check the `examples/` directory for sample input files:
- `flowchart_example.txt` - Process flow example
- `diagram_example.txt` - System architecture example  
- `chart_example.txt` - Data visualization example

## Configuration

Edit `config.json` to customize:
- Server port and host
- Default visual type
- Output settings
- Secret redaction options

## Troubleshooting

1. **Port already in use**: Change port in `config.json` or use `--port` flag
2. **Python not found**: Make sure Python 3.8+ is installed and in PATH
3. **Permission denied**: On Mac/Linux, make sure scripts are executable

## Files Created

- `run_local.py` - Main server script
- `start_visual_agent.*` - Platform-specific startup scripts
- `config.json` - Configuration file
- `examples/` - Example input files
- `output/` - Generated visual files
- `logs/` - Server logs
- `temp/` - Temporary files
"""

    with open("README_LOCAL.md", "w") as f:
        f.write(readme_content)
    print("📚 Created README_LOCAL.md")


def main():
    """Main installation function"""
    print("🚀 Visual Agent - Local Installation")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return 1

    # Create directories
    create_directories()

    # Create startup scripts
    create_startup_scripts()

    # Create example files
    create_example_files()

    # Create config file
    create_config_file()

    # Create local README
    create_readme_local()

    # Test installation
    if not test_installation():
        return 1

    print("\n" + "=" * 50)
    print("🎉 Local installation completed successfully!")
    print("\nQuick start options:")
    print("1. Run server: python run_local.py")
    print("2. Use startup script: ./start_visual_agent.sh (Mac/Linux) or start_visual_agent.bat (Windows)")
    print("3. Check examples: Look in the examples/ directory")
    print("4. Read docs: README_LOCAL.md")

    return 0


if __name__ == "__main__":
    exit(main())
