#!/usr/bin/env python3
"""
Android Emulator Setup Script for Charles Proxy
This script sets up an Android emulator and configures it to use Charles Proxy
"""

import subprocess
import shutil
import os
import sys
import time
import argparse

class AndroidEmulatorSetup:
    def __init__(self, proxy_url="127.0.0.1", proxy_port="8888"):
        self.proxy_url = proxy_url
        self.proxy_port = proxy_port
        self.avd_name = "CharlesProxy_AVD"
        
    def find_adb(self):
        """Find the adb executable path"""
        # Try shutil.which first
        adb_path = shutil.which('adb')
        if adb_path:
            return adb_path
        
        # Try common macOS installation paths
        home = os.path.expanduser('~')
        possible_paths = [
            f'{home}/Library/Android/sdk/platform-tools/adb',
            f'{home}/Android/Sdk/platform-tools/adb',
            '/usr/local/bin/adb',
            '/opt/homebrew/bin/adb',
            '/usr/bin/adb'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def find_emulator(self):
        """Find the emulator executable path"""
        emulator_path = shutil.which('emulator')
        if emulator_path:
            return emulator_path
        
        # Try common Android SDK paths
        home = os.path.expanduser('~')
        possible_paths = [
            f'{home}/Library/Android/sdk/emulator/emulator',
            f'{home}/Android/Sdk/emulator/emulator',
            '/usr/local/bin/emulator',
            '/opt/homebrew/bin/emulator'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def find_avdmanager(self):
        """Find the avdmanager executable path"""
        avdmanager_path = shutil.which('avdmanager')
        if avdmanager_path:
            return avdmanager_path
        
        # Try common Android SDK paths
        home = os.path.expanduser('~')
        possible_paths = [
            f'{home}/Library/Android/sdk/cmdline-tools/latest/bin/avdmanager',
            f'{home}/Library/Android/sdk/tools/bin/avdmanager',
            f'{home}/Android/Sdk/cmdline-tools/latest/bin/avdmanager',
            f'{home}/Android/Sdk/tools/bin/avdmanager',
            '/usr/local/bin/avdmanager',
            '/opt/homebrew/bin/avdmanager'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def check_android_sdk(self):
        """Check if Android SDK is properly configured"""
        print("🔍 Checking Android SDK installation...")
        
        adb_path = self.find_adb()
        emulator_path = self.find_emulator()
        avdmanager_path = self.find_avdmanager()
        
        if not adb_path:
            print("❌ ADB not found. Please install Android Platform-Tools")
            return False
        
        if not emulator_path:
            print("❌ Android emulator not found. Please install Android SDK")
            return False
        
        if not avdmanager_path:
            print("⚠️  AVD Manager not found. Some features may not work")
        
        print(f"✅ ADB found: {adb_path}")
        print(f"✅ Emulator found: {emulator_path}")
        if avdmanager_path:
            print(f"✅ AVD Manager found: {avdmanager_path}")
        
        return True
    
    def list_available_avds(self):
        """List available Android Virtual Devices"""
        print("\n📱 Checking available AVDs...")
        
        # Try emulator command first (more reliable)
        emulator_path = self.find_emulator()
        if emulator_path:
            try:
                result = subprocess.run([emulator_path, '-list-avds'], 
                                     capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    avds = []
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            avds.append(line.strip())
                            print(f"  📱 {line.strip()}")
                    
                    if not avds:
                        print("  No AVDs found")
                    
                    return avds
                else:
                    print(f"❌ Error listing AVDs: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("❌ Timeout while listing AVDs")
            except Exception as e:
                print(f"❌ Error listing AVDs: {e}")
        
        # Fallback to avdmanager if available
        avdmanager_path = self.find_avdmanager()
        if avdmanager_path:
            try:
                result = subprocess.run([avdmanager_path, 'list', 'avd'], 
                                     capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    avds = []
                    for line in result.stdout.split('\n'):
                        if line.strip() and 'Name:' in line:
                            avd_name = line.split('Name:')[1].strip()
                            avds.append(avd_name)
                            print(f"  📱 {avd_name}")
                    
                    if not avds:
                        print("  No AVDs found")
                    
                    return avds
                else:
                    print(f"❌ Error listing AVDs: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("❌ Timeout while listing AVDs")
            except Exception as e:
                print(f"❌ Error listing AVDs: {e}")
        
        return []
    
    def create_avd(self):
        """Create a new Android Virtual Device"""
        print(f"\n🚀 Creating AVD: {self.avd_name}")
        
        # Check if AVD already exists
        existing_avds = self.list_available_avds()
        if self.avd_name in existing_avds:
            print(f"✅ AVD '{self.avd_name}' already exists")
            return True
        
        # Try to create AVD using avdmanager if available
        avdmanager_path = self.find_avdmanager()
        if avdmanager_path:
            try:
                # Use a common system image (API 30 - Android 11)
                cmd = [
                    avdmanager_path, 'create', 'avd',
                    '--name', self.avd_name,
                    '--package', 'system-images;android-30;google_apis;x86_64',
                    '--force'  # Overwrite if exists
                ]
                
                print(f"Running: {' '.join(cmd)}")
                
                # Run the command interactively to handle prompts
                result = subprocess.run(cmd, input=b'no\n', timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ AVD '{self.avd_name}' created successfully")
                    return True
                else:
                    print(f"❌ Failed to create AVD. Return code: {result.returncode}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("❌ Timeout while creating AVD")
                return False
            except Exception as e:
                print(f"❌ Error creating AVD: {e}")
                return False
        else:
            print("⚠️  AVD Manager not found. Cannot create new AVDs.")
            print("💡 You can use an existing AVD or install Android Studio to create new ones.")
            
            # Suggest using an existing AVD
            if existing_avds:
                print(f"\n💡 Available AVDs: {', '.join(existing_avds)}")
                print(f"💡 You can use one of these by specifying --avd-name")
                return False
            else:
                print("❌ No AVDs available and cannot create new ones")
                return False
    
    def start_emulator(self):
        """Start the Android emulator with proxy configuration"""
        print(f"\n🚀 Starting emulator: {self.avd_name}")
        
        emulator_path = self.find_emulator()
        if not emulator_path:
            print("❌ Emulator not found")
            return False
        
        # Start emulator with proxy settings
        emulator_cmd = [
            emulator_path,
            '-avd', self.avd_name,
            '-http-proxy', f'{self.proxy_url}:{self.proxy_port}',
            '-no-snapshot-load',
            '-no-boot-anim',  # Faster boot
            '-gpu', 'swiftshader_indirect',  # Software rendering
            '-memory', '2048',  # 2GB RAM
            '-cores', '2'  # 2 CPU cores
        ]
        
        print(f"Running: {' '.join(emulator_cmd)}")
        print("⏳ Starting emulator (this may take a few minutes)...")
        
        try:
            # Start emulator in background
            process = subprocess.Popen(emulator_cmd, 
                                    cwd=os.path.dirname(emulator_path),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            
            print(f"✅ Emulator process started (PID: {process.pid})")
            print("💡 The emulator will boot up in a few minutes")
            print("💡 You can monitor progress in the emulator window")
            
            return process
            
        except Exception as e:
            print(f"❌ Error starting emulator: {e}")
            return False
    
    def wait_for_device(self, timeout=120):
        """Wait for the emulator device to be ready"""
        print(f"\n⏳ Waiting for device to be ready (timeout: {timeout}s)...")
        
        adb_path = self.find_adb()
        if not adb_path:
            print("❌ ADB not found")
            return False
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run([adb_path, 'wait-for-device'], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✅ Device is ready!")
                    return True
            except subprocess.TimeoutExpired:
                pass
            
            # Check if device is listed
            try:
                result = subprocess.run([adb_path, 'devices'], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and 'device' in result.stdout:
                    print("✅ Device detected and ready!")
                    return True
            except subprocess.TimeoutExpired:
                pass
            
            print("⏳ Still waiting for device...")
            time.sleep(5)
        
        print("❌ Timeout waiting for device")
        return False
    
    def configure_proxy(self):
        """Configure proxy settings on the Android device"""
        print(f"\n🔧 Configuring proxy: {self.proxy_url}:{self.proxy_port}")
        
        adb_path = self.find_adb()
        if not adb_path:
            print("❌ ADB not found")
            return False
        
        proxy_settings = f"{self.proxy_url}:{self.proxy_port}"
        
        # Method 1: Try using Android settings database
        print("📱 Method 1: Using Android settings database...")
        try:
            result = subprocess.run([adb_path, 'shell', 'settings', 'put', 'global', 'http_proxy', proxy_settings], 
                                 capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ Proxy configured via settings: {proxy_settings}")
                return True
            else:
                print(f"⚠️  Settings method failed: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Settings method error: {e}")
        
        # Method 2: Try using iptables (requires root)
        print("📱 Method 2: Using iptables (requires root)...")
        try:
            # HTTP proxy
            result = subprocess.run([adb_path, 'shell', 'su', '-c', 
                                  f'iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination {self.proxy_url}:{self.proxy_port}'], 
                                 capture_output=True, text=True, timeout=30)
            
            # HTTPS proxy
            result2 = subprocess.run([adb_path, 'shell', 'su', '-c', 
                                   f'iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination {self.proxy_url}:{self.proxy_port}'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result2.returncode == 0:
                print(f"✅ Proxy configured via iptables: {proxy_settings}")
                return True
            else:
                print(f"⚠️  iptables method failed")
        except Exception as e:
            print(f"⚠️  iptables method error: {e}")
        
        print("⚠️  Automatic proxy configuration failed")
        print("💡 You may need to configure proxy manually in device settings:")
        print("   Settings > Wi-Fi > Long press network > Modify network > Advanced options > Proxy")
        print(f"   Hostname: {self.proxy_url}")
        print(f"   Port: {self.proxy_port}")
        
        return False
    
    def test_proxy_connection(self):
        """Test if the proxy connection is working"""
        print(f"\n🧪 Testing proxy connection to {self.proxy_url}:{self.proxy_port}")
        
        adb_path = self.find_adb()
        if not adb_path:
            print("❌ ADB not found")
            return False
        
        try:
            # Test HTTP connection through proxy
            test_cmd = [
                adb_path, 'shell', 'curl', '-x', f'{self.proxy_url}:{self.proxy_port}',
                '--connect-timeout', '10', 'http://httpbin.org/ip'
            ]
            
            print(f"Testing with: {' '.join(test_cmd)}")
            
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Proxy connection test successful!")
                print(f"Response: {result.stdout[:200]}...")
                return True
            else:
                print(f"❌ Proxy connection test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Proxy connection test timeout")
            return False
        except Exception as e:
            print(f"❌ Proxy connection test error: {e}")
            return False
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Android Emulator Setup for Charles Proxy")
        print("=" * 50)
        print(f"Proxy: {self.proxy_url}:{self.proxy_port}")
        print(f"AVD Name: {self.avd_name}")
        print()
        
        # Check prerequisites
        if not self.check_android_sdk():
            print("\n❌ Setup cannot continue. Please install Android SDK and Platform-Tools")
            return False
        
        # List existing AVDs
        self.list_available_avds()
        
        # Create AVD if needed, or use existing one
        if not self.create_avd():
            # Check if we can use an existing AVD
            existing_avds = self.list_available_avds()
            if existing_avds:
                # Prefer the Charles-specific AVD if it exists
                charles_avd = None
                for avd in existing_avds:
                    if 'charles' in avd.lower():
                        charles_avd = avd
                        break
                
                if charles_avd:
                    print(f"\n💡 Found perfect AVD for Charles Proxy: {charles_avd}")
                    self.avd_name = charles_avd
                else:
                    print(f"\n💡 Using existing AVD: {existing_avds[0]}")
                    self.avd_name = existing_avds[0]
            else:
                print("\n❌ No AVDs available and cannot create new ones")
                return False
        
        # Start emulator
        emulator_process = self.start_emulator()
        if not emulator_process:
            print("\n❌ Failed to start emulator")
            return False
        
        # Wait for device
        if not self.wait_for_device():
            print("\n❌ Device not ready within timeout")
            return False
        
        # Configure proxy
        if not self.configure_proxy():
            print("\n⚠️  Proxy configuration may need manual setup")
        
        # Test proxy connection
        if self.test_proxy_connection():
            print("\n🎉 Setup completed successfully!")
            print("💡 Your Android emulator is now configured to use Charles Proxy")
            print("💡 All network traffic will be visible in Charles Proxy")
        else:
            print("\n⚠️  Setup completed with warnings")
            print("💡 Proxy may need manual configuration in device settings")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Setup Android Emulator with Charles Proxy')
    parser.add_argument('--proxy-url', default='127.0.0.1', help='Proxy URL (default: 127.0.0.1)')
    parser.add_argument('--proxy-port', default='8888', help='Proxy port (default: 8888)')
    parser.add_argument('--avd-name', default='CharlesProxy_AVD', help='AVD name (default: CharlesProxy_AVD)')
    
    args = parser.parse_args()
    
    setup = AndroidEmulatorSetup(args.proxy_url, args.proxy_port)
    setup.avd_name = args.avd_name
    
    try:
        success = setup.run_setup()
        if success:
            print("\n✅ Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 