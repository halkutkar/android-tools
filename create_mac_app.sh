#!/bin/bash

# Script to create a macOS app bundle for DoorDash API GUI

APP_NAME="DoorDash API GUI"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Creating macOS app bundle for DoorDash API GUI..."

# Create the app bundle structure
mkdir -p "${APP_NAME}.app/Contents/MacOS"
mkdir -p "${APP_NAME}.app/Contents/Resources"

# Create Info.plist
cat > "${APP_NAME}.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DoorDash API GUI</string>
    <key>CFBundleIdentifier</key>
    <string>com.doordash.api.gui</string>
    <key>CFBundleName</key>
    <string>DoorDash API GUI</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>
EOF

# Create the main executable script
cat > "${APP_NAME}.app/Contents/MacOS/DoorDash API GUI" << 'EOF'
#!/bin/bash

# Get the directory containing this app bundle
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"

# Change to the scripts directory
cd "$APP_DIR"

# Launch the GUI
./launch_gui.sh
EOF

# Make the executable script executable
chmod +x "${APP_NAME}.app/Contents/MacOS/DoorDash API GUI"

echo "✅ Created ${APP_NAME}.app"
echo "📋 To install:"
echo "   1. Copy '${APP_NAME}.app' to your Applications folder"
echo "   2. Double-click to launch the DoorDash API GUI"
echo ""
echo "💡 You can also drag it to your Dock for quick access!" 