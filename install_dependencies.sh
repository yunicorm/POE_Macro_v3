#!/bin/bash
# POE Macro v3.0 Dependencies Installation Script

echo "Installing POE Macro v3.0 dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python packages..."
pip install --upgrade pip

# Core dependencies
pip install opencv-python==4.9.0.80
pip install numpy==1.26.4
pip install PyQt5==5.15.10
pip install PyYAML==6.0.1
pip install python-dotenv==1.0.0
pip install pillow==10.2.0
pip install pyautogui==0.9.54
pip install pynput==1.7.6
pip install psutil==5.9.8
pip install requests==2.31.0
pip install colorama==0.4.6
pip install mss==9.0.1

echo "Installation complete!"
echo "To activate the environment, run: source venv/bin/activate"
