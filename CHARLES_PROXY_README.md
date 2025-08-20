# Charles Proxy Integration with Android Emulator

This feature allows you to set up an Android emulator to route all network traffic through Charles Proxy for debugging and analyzing API calls.

## 🌟 Features

### GUI Integration
- **Charles Proxy Tab**: New configuration tab in the DoorDash API GUI
- **Proxy Settings**: Configure proxy URL and port (default: 127.0.0.1:8888)
- **AVD Selection**: Choose which Android Virtual Device to use
- **Auto-detection**: Automatically find and suggest the best AVD for Charles Proxy
- **Real-time Status**: Live updates on emulator and proxy configuration status

### Standalone Script
- **`setup_android_emulator.py`**: Command-line tool for emulator setup
- **Cross-platform**: Works on macOS, Linux, and Windows
- **Smart AVD Detection**: Automatically finds existing AVDs
- **Proxy Configuration**: Multiple methods for setting up proxy on device

## 🚀 Quick Start

### Option 1: GUI (Recommended)
1. Open the DoorDash API GUI
2. Go to the "🌐 Charles Proxy" tab
3. Set your proxy URL and port (default: 127.0.0.1:8888)
4. Click "🔍 Auto-detect" to find available AVDs
5. Click "🚀 Start Emulator" to launch with proxy settings

### Option 2: Command Line
```bash
# Basic setup with default settings
python3 setup_android_emulator.py

# Custom proxy configuration
python3 setup_android_emulator.py --proxy-url 192.168.1.100 --proxy-port 8080

# Use specific AVD
python3 setup_android_emulator.py --avd-name Pixel_9_Pro_-_Charles
```

## 📱 Prerequisites

### Required Tools
- **Android SDK**: For emulator and ADB commands
- **Charles Proxy**: Running on your machine
- **Python 3.7+**: For the setup scripts

### Installation
```bash
# macOS (using Homebrew)
brew install android-platform-tools

# Or download Android Studio which includes all tools
# https://developer.android.com/studio
```

## 🔧 Configuration

### Proxy Settings
- **URL**: Usually `127.0.0.1` for local machine
- **Port**: Default Charles Proxy port is `8888`
- **Protocol**: Supports HTTP and HTTPS traffic

### AVD Selection
The system automatically detects available AVDs and suggests the best one:
- **Priority 1**: AVDs with "charles" in the name
- **Priority 2**: First available AVD
- **Fallback**: Manual AVD name entry

## 🎯 How It Works

### 1. Emulator Launch
- Starts Android emulator with `-http-proxy` flag
- Configures emulator to route traffic through specified proxy
- Optimized settings for faster boot and better performance

### 2. Proxy Configuration
- **Method 1**: Android settings database (most reliable)
- **Method 2**: iptables rules (requires root access)
- **Fallback**: Manual configuration in device settings

### 3. Traffic Routing
- All HTTP/HTTPS traffic from emulator goes through Charles Proxy
- Enables inspection of API calls, network requests, and responses
- Perfect for debugging mobile app network behavior

## 🛠️ Troubleshooting

### Common Issues

#### "ADB not found"
```bash
# Check if Android tools are in PATH
which adb
which emulator

# Add to PATH if needed
export PATH=$PATH:~/Library/Android/sdk/platform-tools
export PATH=$PATH:~/Library/Android/sdk/emulator
```

#### "More than one device/emulator"
- Multiple emulators are running
- The system will automatically target the correct device
- You can manually specify device using `adb -s <device_id>`

#### "Proxy configuration failed"
- Try manual configuration in device settings
- Ensure Charles Proxy is running and accessible
- Check firewall settings

### Manual Proxy Setup
If automatic configuration fails:
1. Go to **Settings > Wi-Fi** on the emulator
2. Long press the connected network
3. Select **Modify network**
4. Check **Advanced options**
5. Set **Proxy** to **Manual**
6. Enter your proxy hostname and port

## 📊 Monitoring

### Status Indicators
- **Ready**: System ready to start emulator
- **Starting**: Emulator is launching
- **Device Ready**: Emulator is booted and ready
- **Configuring**: Setting up proxy settings
- **Complete**: Setup finished successfully

### Logs
- Check the status display in the GUI
- Monitor terminal output for detailed information
- Use `adb logcat` for device-level logs

## 🔒 Security Notes

- **Local Network Only**: Proxy should only be accessible from local network
- **Development Use**: This setup is for development/testing only
- **No Production**: Don't use this configuration in production apps

## 🎉 Success Indicators

When everything is working correctly:
- ✅ Emulator starts successfully
- ✅ Device is detected by ADB
- ✅ Proxy settings are applied
- ✅ Network traffic appears in Charles Proxy
- ✅ API calls from the app are visible in Charles

## 📚 Additional Resources

- [Charles Proxy Documentation](https://www.charlesproxy.com/documentation/)
- [Android Emulator Documentation](https://developer.android.com/studio/run/emulator)
- [ADB Command Reference](https://developer.android.com/studio/command-line/adb)

## 🤝 Support

If you encounter issues:
1. Check the status messages in the GUI
2. Verify Android SDK installation
3. Ensure Charles Proxy is running
4. Check network connectivity between emulator and host machine
5. Review the troubleshooting section above 