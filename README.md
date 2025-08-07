# DoorDash API GUI Application

A modern Python GUI application for testing the DoorDash realtime recommendation API with an intuitive interface.

## 🚀 Quick Start

### Option 1: Use the Launcher Script (Recommended)
```bash
./launch_gui.sh
```

### Option 2: Manual Launch
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

### 📋 Headers Tab
- **Cookies & Session**: HTTP cookies, session IDs, request IDs
- **Facets & Features**: API facets version, feature store variants
- **Localization**: Language and locale settings

### 📍 Location Tab
- **Geographic Coordinates**: Latitude and longitude
- **Market Information**: Submarket and district IDs
- **Device & Context**: Device identifiers and location context

### ⚙️ Advanced Tab
- **Events & Data**: Realtime events JSON configuration
- **API Configuration**: Error formats, feature flags
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
   - Watch the progress bar during the request
   - View results in the tabbed interface

6. **Analyze Results**
   - **Summary**: Quick overview of response status and metrics
   - **Raw Response**: Complete JSON data (if verbose enabled)
   - **Carousel Titles**: Parsed and numbered list of found carousels

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
2. **Command Line**: Use `--token=YOUR_TOKEN` or `-t YOUR_TOKEN`
3. **Config File**: Set `AUTHORIZATION_TOKEN='your_token'` in `config.env` (not recommended for shared repos)

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