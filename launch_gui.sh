#!/bin/bash

# =====================================================
# DoorDash API GUI Launcher
# =====================================================
# This script activates the virtual environment and
# launches the Python GUI application

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting DoorDash API GUI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    echo "📥 Installing dependencies..."
    source venv/bin/activate
    pip install requests
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

# Check if config file exists
if [ ! -f "config.env" ]; then
    echo "❌ config.env file not found!"
    echo "Please ensure config.env is in the same directory as this script."
    exit 1
fi

echo "🎯 Launching GUI application..."
python3 doordash_api_gui.py

echo "👋 GUI application closed." 