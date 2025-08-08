#!/bin/bash

# DoorDash API GUI Launcher Script
# This script launches the DoorDash API GUI application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Launch the GUI using the existing launcher
./launch_gui.sh 