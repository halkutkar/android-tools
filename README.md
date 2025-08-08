# DoorDash API GUI Application

A modern Python GUI application for testing the DoorDash realtime recommendation API with an intuitive interface.

## ✨ Latest Features

### 🎯 Client Configuration Presets
- **📱 iOS Prod**: Production iOS app configuration (v7.26.1)
- **🤖 Android Prod**: Production Android app configuration (v15.227.5)
- **🛠️ Android Debug**: Debug Android build configuration (v16.0.0)
- **🌐 Web Chrome**: Browser-based testing with Chrome 138 user agent

### 📍 Office Location Presets
- **🏢 SF Office**: San Francisco office coordinates (303 2nd Street, Marathon Plaza)
- **🗽 NY Office**: New York office coordinates (200 5th Avenue, Flatiron District)

### 🔧 Enhanced API Controls
- **Cursor Management**: Configurable pagination cursor for `/v3/feed/homepage` endpoint
- **Conditional Parameters**: Smart parameter inclusion (only send cursor when configured)
- **Improved Layout**: Larger interface (1500x1000px) with better space utilization

## 🚀 Quick Start

### Option 1: macOS App (Easiest)
```bash
# Create the macOS app bundle
./create_mac_app.sh

# Copy to Applications folder
cp -r "DoorDash API GUI.app" /Applications/

# Launch from Applications or Dock
open /Applications/"DoorDash API GUI.app"
```

### Option 2: Use the Launcher Script
```bash
./launch_gui.sh
```

### Option 3: Manual Launch
```bash
# Activate virtual environment
source venv/bin/activate

# Run the GUI
python3 doordash_api_gui.py
```

## 📋 Prerequisites

- Python 3.7 or higher
- macOS with tkinter support (usually included)
- `config.env` file with API configuration

## 🍎 macOS App Installation

For the easiest experience, create a native macOS app:

1. **Create the App Bundle**:
   ```bash
   ./create_mac_app.sh
   ```

2. **Install to Applications**:
   ```bash
   cp -r "DoorDash API GUI.app" /Applications/
   ```

3. **Launch Like Any Mac App**:
   - Find "DoorDash API GUI" in Applications folder
   - Double-click to launch
   - Drag to Dock for quick access
   - Use Spotlight search: `⌘ + Space` → "DoorDash API GUI"

### 🛠️ macOS App Troubleshooting

If the app doesn't launch:

1. **Check Dependencies**: Ensure Python 3 and required packages are installed
   ```bash
   python3 --version
   pip3 install requests
   ```

2. **Run from Terminal First**: Test the script version works
   ```bash
   cd /path/to/scripts
   ./launch_gui.sh
   ```

3. **Permission Issues**: If you get permission denied errors
   ```bash
   # Re-create the app bundle
   ./create_mac_app.sh
   
   # Make sure the executable is set correctly  
   chmod +x "DoorDash API GUI.app/Contents/MacOS/DoorDash API GUI"
   ```

4. **Manual Launch**: You can always run directly:
   ```bash
   cd /path/to/scripts
   python3 doordash_api_gui.py
   ```

## 🎯 Features

### Advanced Configuration Management
- ✅ **Complete Configuration Editor**: Edit all configuration values through organized tabs
- ✅ **Tabbed Interface**: Organized into API Settings, Headers, Location, and Advanced sections
- ✅ **Real-time Editing**: Make changes in GUI and use immediately
- ✅ **File Management**: Save to file, reload from file, or reset changes
- ✅ **Validation**: Input validation and secure token handling
- ✅ **Backup Creation**: Automatic backup when saving to file

### Request Controls
- ✅ One-click API requests with progress indication
- ✅ Configurable verbose mode for detailed responses
- ✅ Auto-parsing of carousel titles
- ✅ Clear response function
- ✅ **Export as cURL**: Generate ready-to-use curl commands for terminal/debugging
- ✅ Uses current GUI configuration values for requests

### Response Display
The GUI provides three organized tabs for viewing results:

#### 📈 Summary Tab
- HTTP status code and response details
- Request performance metrics
- Response size and content type
- Timestamp information

#### 📋 Raw Response Tab
- Complete JSON response (when verbose mode is enabled)
- Formatted and syntax-highlighted output
- Raw text fallback for non-JSON responses

#### 🎠 Carousel Titles Tab
- Automatically extracted carousel titles
- Numbered list with count summary
- Handles both JSON parsing and regex fallback

### User Experience
- 🎨 Modern, clean interface with emojis
- 📊 Real-time status updates
- 🔄 Progress indicators during requests
- ❌ Error handling with user-friendly messages
- 🖥️ Responsive layout that scales properly
- 🚀 Enhanced UI with larger window size (1500x1000px)
- ⚡ One-click preset configurations for common scenarios

## 🛠️ Technical Details

### Dependencies
- `tkinter` - GUI framework (built into Python)
- `requests` - HTTP library for API calls
- `json` - JSON parsing (built into Python)
- `threading` - Non-blocking API requests
- `re` - Regular expressions for parsing

### Architecture
- **Main Class**: `DoorDashAPIGUI` - Handles all GUI logic
- **Threading**: API requests run in separate threads to keep GUI responsive
- **Configuration**: Loads from `config.env` file in the same directory
- **Error Handling**: Comprehensive error handling with user feedback

### File Structure
```
scripts/
├── doordash_api_gui.py      # Main GUI application
├── launch_gui.sh            # Launcher script
├── config.env               # Configuration file
├── requirements.txt         # Python dependencies
├── venv/                    # Virtual environment
└── README.md               # This file
```

## 🔧 Configuration Editor

The GUI now includes a comprehensive configuration editor with organized tabs:

### 🌐 API Settings Tab
- **API Host**: DoorDash API hostname
- **Authorization Token**: JWT authentication token (masked input)
- **Experience ID**: Application experience identifier
- **User Agent**: Client user agent string
- **Client Version**: Application version
- **Client Presets**: One-click configurations for different platforms:
  - 📱 **iOS Prod**: DoordashConsumer/7.26.1 (iPhone; iOS 18.5)
  - 🤖 **Android Prod**: DoorDashConsumer/Android 15.227.5
  - 🛠️ **Android Debug**: DoorDashConsumer/Android 16.0.0-prod-debug
  - 🌐 **Web Chrome**: Chrome 138.0.0.0 browser user agent

### 📋 Headers Tab
- **Cookies & Session**: HTTP cookies, session IDs, request IDs
- **Facets & Features**: API facets version, feature store variants
- **Localization**: Language and locale settings

### 📍 Location Tab
- **Geographic Coordinates**: Latitude and longitude with location presets:
  - 🏢 **SF Office**: 303 2nd Street, San Francisco CA (Marathon Plaza)
  - 🗽 **NY Office**: 200 5th Avenue, New York NY (Flatiron District)
- **Market Information**: Submarket and district IDs
- **Device & Context**: Device identifiers and location context

### ⚙️ Advanced Tab
- **Events & Data**: Realtime events JSON configuration
- **API Configuration**: Error formats, feature flags, pagination cursor
- **Cursor Control**: Configurable cursor parameter for `/v3/feed/homepage` endpoint
- **Display Settings**: Verbose mode defaults, output limits

### Configuration Management
- **Real-time Editing**: Changes take effect immediately for API requests
- **Memory vs File**: Save to memory for session use, or persist to file
- **Backup Safety**: Automatic backup creation when saving to file
- **Reset Capability**: Easily revert changes back to file values

## 🎮 How to Use

### GUI Application

1. **Launch the Application**
   ```bash
   ./launch_gui.sh
   ```

2. **Configure Settings** (comprehensive configuration editor)
   - **🌐 API Settings**: Host, auth token, client info
   - **📋 Headers**: Cookies, session IDs, facets configuration
   - **📍 Location**: Coordinates, market info, device context
   - **⚙️ Advanced**: Events, API options, display settings

3. **Manage Configuration**
   - **💾 Save Configuration**: Save changes to memory for immediate use
   - **🔄 Reset to File**: Discard changes and reload from file
   - **📁 Save to File**: Permanently save changes to config.env (creates backup)

4. **Configure Request Options**
   - Check "Show detailed response" for full JSON output
   - Check "Auto-parse carousel titles" for automatic extraction

5. **Make API Request**
   - Click "🚀 Make API Request" (uses current GUI settings)
   - Or click "📋 Export as cURL" to generate a command for terminal use
   - Watch the progress bar during the request
   - View results in the tabbed interface

6. **Analyze Results**
   - **Summary**: Quick overview of response status and metrics
   - **Raw Response**: Complete JSON data (if verbose enabled)
   - **Carousel Titles**: Parsed and numbered list of found carousels

7. **Export for Terminal Use**
   - Click "📋 Export as cURL" to generate a curl command
   - Copy to clipboard for use in terminal or scripts
   - Includes all current headers, parameters, and authentication
   - Handles both GET and POST requests (experiments endpoint)

### Command Line Script

You can also use the bash script directly:

```bash
# Basic usage (will prompt for token if not set)
./realtime_test_with_config.sh

# With verbose output
./realtime_test_with_config.sh --verbose

# Set token via command line
./realtime_test_with_config.sh --token=YOUR_JWT_TOKEN

# Short form
./realtime_test_with_config.sh -t YOUR_JWT_TOKEN

# Show help
./realtime_test_with_config.sh --help
```

## 🚨 Troubleshooting

### GUI Won't Start
- Ensure Python 3.7+ is installed: `python3 --version`
- Check if tkinter is available: `python3 -c "import tkinter"`
- Verify config file exists: `ls -la config.env`

### API Request Fails
- Check your internet connection
- Verify the authorization token is not expired
- Ensure all required configuration values are set
- Check the status bar for specific error messages

### Dependencies Issues
- The launcher script automatically handles virtual environment setup
- If manual setup is needed: `python3 -m venv venv && source venv/bin/activate && pip install requests`

## 🔐 Authorization Token Security

For security, the default configuration sets the authorization token to `null`. This means:

- **No hardcoded tokens**: Tokens are not stored in the repository
- **Runtime input**: You'll be prompted to enter the token when needed
- **Multiple input methods**: 
  - GUI dialog with masked input
  - Command line arguments
  - Interactive prompt in terminal
- **Session-only storage**: Tokens are only kept in memory during execution

### Setting Your Token

1. **In GUI**: Click "🔑 Set Auth Token" or you'll be prompted on first request
   - **Option 1 (Recommended)**: Use "🌐 Open Dev Console" to create a test consumer account
   - **Option 2**: Capture from Charles Proxy or existing requests
2. **Command Line**: Use `--token=YOUR_TOKEN` or `-t YOUR_TOKEN`
3. **Config File**: Set `AUTHORIZATION_TOKEN='your_token'` in `config.env` (not recommended for shared repos)
4. **Dev Console**: Visit [DoorDash Dev Console](https://devconsole.doordash.team/test-studio/test-accounts) to create test accounts and get JWTs

## 💡 Tips

- **Keep Token Updated**: JWT tokens expire, get fresh tokens as needed
- **Use Verbose Mode**: Enable detailed response to see the complete API response
- **Monitor Status Bar**: Real-time updates show current operation status
- **Clear Between Requests**: Use "🗑️ Clear Response" to reset display between tests
- **Token Security**: Never commit real tokens to version control

## 🔄 Updates

To update the configuration:
1. Edit `config.env` file
2. Click "🔄 Reload Config" in the GUI
3. No need to restart the application

The GUI provides a much more user-friendly way to test the DoorDash API compared to command-line tools, with visual feedback, organized output, and easy configuration management. 