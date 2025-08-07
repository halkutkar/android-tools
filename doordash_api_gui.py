#!/usr/bin/env python3
"""
DoorDash API GUI Application
A modern GUI for testing DoorDash realtime recommendation API
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
import os
from datetime import datetime
import re

class DoorDashAPIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DoorDash API Tester & Configuration Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration variables
        self.config = {}
        self.load_config()
        
        # Create GUI components
        self.create_widgets()
        
        # Status variables
        self.is_loading = False
        
    def load_config(self):
        """Load configuration from config.env file"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.env')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip("'\"")
                        self.config[key] = value
        else:
            messagebox.showerror("Config Error", "config.env file not found!")
            
        # Check if authorization token is null or empty
        if not self.config.get('AUTHORIZATION_TOKEN') or self.config.get('AUTHORIZATION_TOKEN') == 'null':
            self.config['AUTHORIZATION_TOKEN'] = None
            
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Warning/Error banner at the top
        self.create_warning_banner(main_frame)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 DoorDash API Tester & Configuration Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Configuration section
        self.create_config_section(main_frame)
        
        # Request controls
        self.create_controls_section(main_frame)
        
        # Response area with tabs
        response_frame = ttk.Frame(main_frame)
        response_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create notebook for different response views
        self.response_notebook = ttk.Notebook(response_frame)
        self.response_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Request Details tab
        self.request_tab = ttk.Frame(self.response_notebook)
        self.response_notebook.add(self.request_tab, text="📋 Request Details")
        
        self.request_display = scrolledtext.ScrolledText(self.request_tab, wrap=tk.WORD, 
                                                       font=('Consolas', 10))
        self.request_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Carousel Titles tab
        self.carousel_tab = ttk.Frame(self.response_notebook)
        self.response_notebook.add(self.carousel_tab, text="🎠 Carousel Titles")
        
        self.response_display = scrolledtext.ScrolledText(self.carousel_tab, wrap=tk.WORD, 
                                                        font=('Consolas', 10))
        self.response_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Response Summary tab
        self.summary_tab = ttk.Frame(self.response_notebook)
        self.response_notebook.add(self.summary_tab, text="📊 Response Summary")
        
        self.summary_display = scrolledtext.ScrolledText(self.summary_tab, wrap=tk.WORD, 
                                                       font=('Consolas', 10))
        self.summary_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Raw Response tab
        self.raw_tab = ttk.Frame(self.response_notebook)
        self.response_notebook.add(self.raw_tab, text="🔍 Raw Response")
        
        self.raw_display = scrolledtext.ScrolledText(self.raw_tab, wrap=tk.WORD, 
                                                   font=('Consolas', 10))
        self.raw_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_warning_banner(self, parent):
        """Create a warning/error banner at the top of the main window"""
        self.warning_frame = ttk.Frame(parent)
        self.warning_frame.pack(fill=tk.X, pady=(0, 10))
        
        # This will be updated based on application state
        self.warning_label = None
        self.update_warning_banner()
        
    def update_warning_banner(self):
        """Update the warning banner based on current application state"""
        # Clear existing warning label
        if self.warning_label:
            self.warning_label.destroy()
            
        # Check for various warning conditions
        warnings = []
        
        # Check authorization token
        if not self.config.get('AUTHORIZATION_TOKEN') or self.config.get('AUTHORIZATION_TOKEN') == 'null':
            warnings.append("⚠️ Authorization token not set - Click 'Set Auth Token' or configure in API Settings tab")
        
        # Check for required configuration
        if not self.config.get('API_BASE_URL'):
            warnings.append("⚠️ API Base URL not configured")
            
        if not self.config.get('API_ENDPOINT_PATH'):
            warnings.append("⚠️ API Endpoint Path not configured")
            
        if not self.config.get('REALTIME_EVENTS'):
            warnings.append("⚠️ No realtime events configured")
        
        # Display warnings if any exist
        if warnings:
            warning_text = "\n".join(warnings)
            self.warning_label = ttk.Label(
                self.warning_frame, 
                text=warning_text,
                foreground='#d9534f',  # Red color for warnings
                font=('Arial', 10, 'bold'),
                background='#f2dede',  # Light red background
                padding=(10, 5),
                relief='solid',
                borderwidth=1,
                wraplength=800
            )
            self.warning_label.pack(fill=tk.X, padx=2, pady=2)
        else:
            # Show success message when all is configured
            self.warning_label = ttk.Label(
                self.warning_frame,
                text="✅ Configuration looks good - Ready to make API requests",
                foreground='#5cb85c',  # Green color for success
                font=('Arial', 10, 'bold'),
                background='#dff0d8',  # Light green background
                padding=(10, 5),
                relief='solid',
                borderwidth=1
            )
            self.warning_label.pack(fill=tk.X, padx=2, pady=2)
        
    def create_config_section(self, parent):
        """Create configuration editing section"""
        config_frame = ttk.LabelFrame(parent, text="📋 Configuration Editor", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create notebook for organized config sections
        self.config_notebook = ttk.Notebook(config_frame)
        self.config_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initialize config variables dictionary
        self.config_vars = {}
        
        # Create different tabs for organized configuration
        self.create_api_config_tab()
        self.create_headers_config_tab()
        self.create_location_config_tab()
        self.create_misc_config_tab()
        
        # Config buttons frame
        config_buttons_frame = ttk.Frame(config_frame)
        config_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(config_buttons_frame, text="💾 Save Configuration", 
                  command=self.save_configuration).pack(side=tk.LEFT)
        ttk.Button(config_buttons_frame, text="🔄 Reset to File", 
                  command=self.reset_configuration).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(config_buttons_frame, text="📁 Save to File", 
                  command=self.save_to_file).pack(side=tk.LEFT, padx=(10, 0))
                
    def create_controls_section(self, parent):
        """Create the control buttons section"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Make Request button
        self.make_request_btn = ttk.Button(controls_frame, text="🚀 Make Request", 
                                         command=self.make_request_threaded, style='Accent.TButton')
        self.make_request_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear Response button
        ttk.Button(controls_frame, text="🧹 Clear Response", 
                  command=self.clear_response).pack(side=tk.LEFT, padx=(0, 10))
        
        # Verbose mode checkbox
        self.verbose_var = tk.BooleanVar(value=True)  # Default to verbose mode
        ttk.Checkbutton(controls_frame, text="Verbose Output", 
                       variable=self.verbose_var).pack(side=tk.LEFT, padx=(0, 10))
        
        # Set Token button
        ttk.Button(controls_frame, text="🔑 Set Auth Token", 
                  command=self.set_auth_token).pack(side=tk.RIGHT)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()
        
    def validate_auth_token(self):
        """Validate that authorization token is set"""
        token = self.config.get('AUTHORIZATION_TOKEN', '')
        if not token or token.lower() == 'null' or not token.strip():
            # Show token input dialog
            self.set_auth_token()
            # Re-check after dialog
            token = self.config.get('AUTHORIZATION_TOKEN', '')
            if not token or token.lower() == 'null' or not token.strip():
                raise Exception("Authorization token is required but not set")
                
    def set_auth_token(self):
        """Show dialog to set authorization token"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Authorization Token")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔑 Set Authorization Token", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, text="""🔍 To find your JWT token:

1. Open Charles Proxy and capture DoorDash API requests
2. Look for the 'authorization' header in any request  
3. Copy ONLY the part after 'JWT ' (without the JWT prefix)

Example: authorization: JWT eyJhbGciOiJIUzI1NiJ9...
Copy: eyJhbGciOiJIUzI1NiJ9...

Paste your token below (JWT prefix will be automatically removed):""", 
                               justify=tk.LEFT, wraplength=500)
        instructions.pack(pady=(0, 20))
        
        # Token entry
        token_label = ttk.Label(main_frame, text="Authorization Token:")
        token_label.pack(anchor=tk.W)
        
        token_var = tk.StringVar()
        token_entry = ttk.Entry(main_frame, textvariable=token_var, width=70, font=('Consolas', 10))
        token_entry.pack(fill=tk.X, pady=(5, 20))
        token_entry.focus()
        
        def save_token():
            token = token_var.get().strip()
            if token:
                # Remove JWT prefix if present and clean up
                if token.startswith('JWT '):
                    token = token[4:].strip()
                elif token.startswith('jwt '):
                    token = token[4:].strip()
                
                self.config['AUTHORIZATION_TOKEN'] = token
                
                # Update the GUI variable if it exists
                if 'AUTHORIZATION_TOKEN' in self.config_vars:
                    self.config_vars['AUTHORIZATION_TOKEN'].set(token)
                
                # Update warning banner
                self.update_warning_banner()
                
                dialog.destroy()
                messagebox.showinfo("Token Set", "✅ Authorization token has been set successfully!")
            else:
                messagebox.showerror("Invalid Token", "Please enter a valid authorization token.")
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="💾 Save Token", command=save_token, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Cancel", command=cancel).pack(side=tk.RIGHT)
        
        # Bind Enter key to save
        dialog.bind('<Return>', lambda e: save_token())
        
    def refresh_config_display(self):
        """Refresh the configuration display section"""
        # Simply update the config variables in the GUI if they exist
        if hasattr(self, 'config_vars'):
            for key, var in self.config_vars.items():
                if key in self.config:
                    var.set(self.config.get(key, ''))
        
        # Update warning banner
        self.update_warning_banner()
        self.update_status("Configuration display refreshed")
                         
    def create_config_field(self, parent, label, key, description="", width=50, is_password=False):
        """Create a configuration field with label and entry"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        # Label
        label_widget = ttk.Label(frame, text=f"{label}:", font=('Arial', 9, 'bold'), width=20)
        label_widget.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clean JWT prefix if this is an authorization token field
        initial_value = self.config.get(key, '')
        if key == 'AUTHORIZATION_TOKEN' and initial_value:
            # Remove JWT prefix if present and trim whitespace
            if initial_value.startswith('JWT '):
                initial_value = initial_value[4:].strip()
            else:
                initial_value = initial_value.strip()
        
        # Entry variable
        var = tk.StringVar(value=initial_value)
        self.config_vars[key] = var
        
        # Entry widget
        entry = ttk.Entry(frame, textvariable=var, width=width, 
                         show="*" if is_password else "")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Description label if provided
        if description:
            desc_label = ttk.Label(frame, text=description, font=('Arial', 8), 
                                 foreground='gray')
            desc_label.pack(side=tk.RIGHT)
            
        return var
        
    def create_api_config_tab(self):
        """Create API configuration tab"""
        api_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(api_frame, text="🌐 API Settings")
        
        # Scrollable frame
        canvas = tk.Canvas(api_frame)
        scrollbar = ttk.Scrollbar(api_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # API configuration fields
        ttk.Label(scrollable_frame, text="🔌 API Connection", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Base URL field
        self.create_api_host_field_with_presets(scrollable_frame)
        
        self.create_config_field(scrollable_frame, "Experience ID", "EXPERIENCE_ID", 
                               "Application experience identifier")
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="🔑 Authentication", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Authorization Token", "AUTHORIZATION_TOKEN", 
                               "JWT Bearer token", is_password=False)
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="📱 Client Information", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "User Agent", "USER_AGENT", 
                               "Client user agent string")
        self.create_config_field(scrollable_frame, "Client Version", "CLIENT_VERSION", 
                               "Application version")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_headers_config_tab(self):
        """Create headers configuration tab"""
        headers_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(headers_frame, text="📋 Headers")
        
        # Scrollable frame
        canvas = tk.Canvas(headers_frame)
        scrollbar = ttk.Scrollbar(headers_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers configuration
        ttk.Label(scrollable_frame, text="🍪 Cookies & Session", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Cookie", "COOKIE", 
                               "HTTP cookies string", width=80)
        self.create_config_field(scrollable_frame, "Session ID", "SESSION_ID", 
                               "Session identifier")
        self.create_config_field(scrollable_frame, "Client Request ID", "CLIENT_REQUEST_ID", 
                               "Unique request identifier")
        self.create_config_field(scrollable_frame, "Correlation ID", "CORRELATION_ID", 
                               "Request correlation ID")
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="🎨 Facets & Features", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Facets Version", "FACETS_VERSION", 
                               "API facets version")
        self.create_config_field(scrollable_frame, "Feature Store", "FACETS_FEATURE_STORE", 
                               "Feature store variant")
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="🌍 Localization", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Accept Language", "ACCEPT_LANGUAGE", 
                               "Preferred language")
        self.create_config_field(scrollable_frame, "User Locale", "USER_LOCALE", 
                               "User locale setting")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_location_config_tab(self):
        """Create location configuration tab"""
        location_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(location_frame, text="📍 Location")
        
        # Scrollable frame
        canvas = tk.Canvas(location_frame)
        scrollbar = ttk.Scrollbar(location_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Location configuration
        ttk.Label(scrollable_frame, text="🗺️ Geographic Coordinates", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Latitude", "LATITUDE", 
                               "Geographic latitude")
        self.create_config_field(scrollable_frame, "Longitude", "LONGITUDE", 
                               "Geographic longitude")
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="🏢 Market Information", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Submarket ID", "SUBMARKET_ID", 
                               "Market subdivision ID")
        self.create_config_field(scrollable_frame, "District ID", "DISTRICT_ID", 
                               "District identifier")
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="📱 Device & Context", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "DD IDs", "DD_IDS", 
                               "Device identifiers JSON", width=80)
        self.create_config_field(scrollable_frame, "Location Context", "DD_LOCATION_CONTEXT", 
                               "Encoded location context", width=80)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_misc_config_tab(self):
        """Create miscellaneous configuration tab"""
        misc_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(misc_frame, text="⚙️ Advanced")
        
        # Scrollable frame
        canvas = tk.Canvas(misc_frame)
        scrollbar = ttk.Scrollbar(misc_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Advanced configuration
        ttk.Label(scrollable_frame, text="🎯 Events & Data", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Special handling for realtime events
        events_frame = ttk.Frame(scrollable_frame)
        events_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(events_frame, text="Realtime Events:", font=('Arial', 9, 'bold'), width=20).pack(side=tk.TOP, anchor=tk.W)
        
        events_var = tk.StringVar(value=self.config.get('REALTIME_EVENTS', ''))
        self.config_vars['REALTIME_EVENTS'] = events_var
        
        events_text = tk.Text(events_frame, height=4, wrap=tk.WORD)
        events_text.pack(fill=tk.X, pady=(5, 0))
        events_text.insert('1.0', events_var.get())
        
        # Bind text widget to variable
        def update_events_var(*args):
            events_var.set(events_text.get('1.0', tk.END).strip())
        events_text.bind('<KeyRelease>', update_events_var)
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="🔧 API Configuration", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "BFF Error Format", "BFF_ERROR_FORMAT", 
                               "Backend error format version")
        self.create_config_field(scrollable_frame, "Support Partner Dashpass", "SUPPORT_PARTNER_DASHPASS", 
                               "Enable partner dashpass support")
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="📊 Display Settings", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Default Verbose", "DEFAULT_VERBOSE", 
                               "Default verbose mode (true/false)")
        self.create_config_field(scrollable_frame, "Max Verbose Lines", "MAX_VERBOSE_LINES", 
                               "Maximum lines in verbose output")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def make_request_threaded(self):
        """Make API request in a separate thread"""
        if self.is_loading:
            return
            
        # Validate auth token first
        try:
            self.validate_auth_token()
        except Exception as e:
            messagebox.showerror("Authorization Error", str(e))
            return
            
        self.is_loading = True
        self.make_request_btn.config(state='disabled')
        # self.progress.start() # Removed progress bar as per new_code
        
        thread = threading.Thread(target=self.make_request)
        thread.daemon = True
        thread.start()
        
    def make_request(self):
        """Make the API request and display response"""
        try:
            # Validate auth token
            self.validate_auth_token()
            
            # Prepare URL with query parameters
            url = f"{self.config.get('API_BASE_URL', '')}{self.config.get('API_ENDPOINT_PATH', '')}"
            
            # Use different parameter formats based on the endpoint
            endpoint_path = self.config.get('API_ENDPOINT_PATH', '')
            if 'unified-gateway' in self.config.get('API_BASE_URL', '') or 'realtime_recommendation' in endpoint_path:
                # Unified Gateway format
                params = {
                    "common_fields.lat": self.config.get("LATITUDE", ""),
                    "common_fields.lng": self.config.get("LONGITUDE", ""),
                    "common_fields.submarket_id": self.config.get("SUBMARKET_ID", ""),
                    "common_fields.district_id": self.config.get("DISTRICT_ID", "")
                }
            else:
                # Consumer BFF format (homepage, feed/me, etc.)
                params = {
                    "lat": self.config.get("LATITUDE", ""),
                    "lng": self.config.get("LONGITUDE", "")
                }
            
            # Add cursor parameter if it exists in realtime events or query
            realtime_events = self.config.get("REALTIME_EVENTS", "")
            if "cursor=" in realtime_events:
                try:
                    import re
                    cursor_match = re.search(r'cursor=([^&\s]+)', realtime_events)
                    if cursor_match:
                        params["cursor"] = cursor_match.group(1)
                except:
                    pass
            
            # Prepare headers
            headers = {
                "Host": self.config.get('API_BASE_URL', '').replace('https://', '').replace('http://', ''),
                "Cookie": self.config.get("COOKIE", ""),
                "authorization": f"JWT {self.config.get('AUTHORIZATION_TOKEN', '')}",
                "accept-language": self.config.get("ACCEPT_LANGUAGE", ""),
                "x-session-id": self.config.get("SESSION_ID", ""),
                "x-client-request-id": self.config.get("CLIENT_REQUEST_ID", ""),
                "x-correlation-id": self.config.get("CORRELATION_ID", ""),
                "client-version": self.config.get("CLIENT_VERSION", ""),
                "user-agent": self.config.get("USER_AGENT", ""),
                "x-experience-id": self.config.get("EXPERIENCE_ID", ""),
                "x-support-partner-dashpass": self.config.get("SUPPORT_PARTNER_DASHPASS", ""),
                "dd-ids": self.config.get("DD_IDS", ""),
                "dd-user-locale": self.config.get("USER_LOCALE", ""),
                "x-bff-error-format": self.config.get("BFF_ERROR_FORMAT", ""),
                "dd-location-context": self.config.get("DD_LOCATION_CONTEXT", ""),
                "x-realtime-recommendation-events": self.config.get("REALTIME_EVENTS", "").split(' cursor=')[0] if ' cursor=' in self.config.get("REALTIME_EVENTS", "") else self.config.get("REALTIME_EVENTS", ""),
                "x-facets-version": self.config.get("FACETS_VERSION", ""),
                "x-facets-feature-store": self.config.get("FACETS_FEATURE_STORE", "")
            }
            
            # Add Consumer BFF specific headers if using Consumer BFF endpoints
            if 'consumer-mobile-bff' in self.config.get('API_BASE_URL', ''):
                headers.update({
                    "x-facets-feature-item-carousel": "true",
                    "x-facets-feature-backend-driven-badges": "true", 
                    "x-facets-feature-no-tile": "true",
                    "x-facets-feature-item-steppers": "true",
                    "x-facets-feature-quick-add-stepper-variant": "true",
                    "x-facets-feature-store-carousel-redesign-round-1": "treatmentVariant2",
                    "x-facets-feature-store-cell-redesign-round-3": "treatmentVariant3",
                    "x-gifting-intent": "false",
                    "traceparent": "00-0779dd623e69dfc82a93b7b553698d95-525a785c689917fe-00",
                    "baggage": "dd-instrumentation.priority=1.0"
                })
            
            # Remove empty headers
            headers = {k: v for k, v in headers.items() if v}
            
            # Show request details
            self.show_request_details(url, params, headers)
            
            # Make the request
            self.update_status("Making API request...")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            # Process the response
            self.process_response(response)
            
        except Exception as e:
            self.handle_request_error(e)
            
    def show_request_details(self, url, params, headers):
        """Display the complete request details in the Request Details tab"""
        self.request_display.delete('1.0', tk.END)
        
        # Build complete URL with parameters
        import urllib.parse
        if params:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
        else:
            full_url = url
        
        # Format request details
        request_details = f"""🚀 API REQUEST DETAILS
{'=' * 50}

📍 REQUEST URL:
{full_url}

🔗 BASE URL: {self.config.get('API_BASE_URL', '')}
📂 ENDPOINT: {self.config.get('API_ENDPOINT_PATH', '')}

📋 QUERY PARAMETERS:
"""
        
        if params:
            for key, value in params.items():
                request_details += f"  • {key}: {value}\n"
        else:
            request_details += "  (No query parameters)\n"
        
        request_details += f"""
🔐 REQUEST HEADERS:
"""
        
        if headers:
            for key, value in headers.items():
                # Truncate very long values for readability
                display_value = value
                if len(str(value)) > 100:
                    display_value = f"{str(value)[:97]}..."
                request_details += f"  • {key}: {display_value}\n"
        else:
            request_details += "  (No headers)\n"
        
        request_details += f"""
⚙️ REQUEST METHOD: GET
🕒 TIMEOUT: 30 seconds
📦 REQUEST BODY: (None for GET request)

{'=' * 50}
ℹ️  This request will be sent to the DoorDash API
"""
        
        self.request_display.insert(tk.END, request_details)
        
        # Set the Request Details tab as active to show the request
        self.response_notebook.select(self.request_tab)
        
    def process_response(self, response):
        """Process and display the API response"""
        try:
            self.update_status(f"Response received: {response.status_code}")
            
            # Clear previous responses
            self.response_display.delete('1.0', tk.END)
            self.summary_display.delete('1.0', tk.END)
            self.raw_display.delete('1.0', tk.END)
            
            # Parse JSON response
            try:
                response_json = response.json()
            except:
                response_json = None
            
            # Extract carousel titles
            carousel_titles = self.extract_carousel_titles(response_json) if response_json else []
            
            # Display carousel titles
            if carousel_titles:
                titles_text = f"🎠 STORE CAROUSEL COMPONENTS FOUND ({len(carousel_titles)} items):\n{'=' * 70}\n\n"
                
                for i, carousel in enumerate(carousel_titles, 1):
                    titles_text += f"🔸 CAROUSEL #{i}\n"
                    titles_text += f"   ID: {carousel['id']}\n"
                    titles_text += f"   Component: {carousel['component_id']} ({carousel['component_category']})\n"
                    titles_text += f"   Text Fields:\n"
                    
                    for field_name, field_value in carousel['text_fields'].items():
                        titles_text += f"     • {field_name}: {field_value}\n"
                    
                    titles_text += "\n"
                
                titles_text += f"{'=' * 70}\n✅ Successfully extracted {len(carousel_titles)} store carousel components"
            else:
                titles_text = "🎠 STORE CAROUSEL COMPONENTS:\n" + "=" * 70 + "\n\n"
                titles_text += "❌ No store carousel components found in response\n\n"
                titles_text += "Looking for components matching:\n"
                titles_text += "• ID pattern: 'carousel.standard:store_carousel*'\n"
                titles_text += "• Component ID: 'carousel.standard'\n"
                titles_text += "• Component Category: 'carousel'\n"
                titles_text += "• With text fields containing content"
            
            self.response_display.insert(tk.END, titles_text)
            
            # Display response summary
            summary = self.create_summary(response)
            self.summary_display.insert(tk.END, summary)
            
            # Display raw response
            if response_json:
                try:
                    import json
                    pretty_json = json.dumps(response_json, indent=2, ensure_ascii=False)
                    self.raw_display.insert(tk.END, pretty_json)
                except:
                    self.raw_display.insert(tk.END, response.text)
            else:
                self.raw_display.insert(tk.END, response.text)
            
            # Switch to the carousel titles tab to show results
            self.response_notebook.select(self.carousel_tab)
            
            self.update_status(f"✅ Request completed successfully - {len(carousel_titles)} carousel titles found")
            
        except Exception as e:
            error_msg = f"❌ Error processing response: {str(e)}"
            self.update_status(error_msg)
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert(tk.END, error_msg)
        finally:
            self.is_loading = False
            self.make_request_btn.config(state='normal')
            # self.progress.stop() # Removed progress bar as per new_code
            
    def create_summary(self, response):
        """Create response summary"""
        summary = f"""🎯 API REQUEST SUMMARY
{'='*50}

📊 Response Details:
  Status Code: {response.status_code}
  Response Size: {len(response.content):,} bytes
  Content Type: {response.headers.get('content-type', 'Unknown')}
  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🌐 Request Details:
  URL: {response.url}
  Method: {response.request.method}
  
📈 Performance:
  Response Time: {response.elapsed.total_seconds():.2f} seconds
  
"""
        
        if response.status_code == 200:
            summary += "✅ Request Status: SUCCESS\n"
            try:
                data = response.json()
                if isinstance(data, dict):
                    summary += f"📦 Response Keys: {', '.join(list(data.keys())[:10])}\n"
                    
                    # Add more detailed info in verbose mode
                    if self.verbose_var.get():
                        summary += f"📋 Total Response Keys: {len(data.keys())}\n"
                        
                        # Show response structure information
                        if 'data' in data:
                            summary += f"📊 Data section present\n"
                        if 'meta' in data:
                            summary += f"📊 Meta section present\n"
                        if 'errors' in data:
                            summary += f"⚠️ Errors section present\n"
                            
            except:
                pass
        else:
            summary += f"❌ Request Status: FAILED\n"
            if self.verbose_var.get():
                summary += f"📋 Error Details: Check Raw Response tab for full error information\n"
            
        summary += f"\n{'='*50}\n"
        return summary
        
    def extract_carousel_titles(self, data):
        """Extract carousel titles from store_carousel components in nested JSON structure"""
        carousels = []
        try:
            if data:
                # Recursively search through the entire JSON structure
                self.find_store_carousels_recursive(data, carousels)
                            
        except Exception as e:
            print(f"Error extracting carousel titles: {e}")
            
        return carousels
        
    def find_store_carousels_recursive(self, obj, carousels):
        """Recursively search through JSON structure to find store carousel components"""
        if isinstance(obj, dict):
            # Check if this object is a store carousel
            if self.is_store_carousel(obj):
                carousel_info = self.extract_store_carousel_info(obj)
                if carousel_info:
                    carousels.append(carousel_info)
            
            # Recursively search through all dictionary values
            for value in obj.values():
                self.find_store_carousels_recursive(value, carousels)
                
        elif isinstance(obj, list):
            # Recursively search through all list items
            for item in obj:
                self.find_store_carousels_recursive(item, carousels)
        
    def is_store_carousel(self, item):
        """Check if item is a store_carousel component"""
        try:
            item_id = item.get('id', '')
            component = item.get('component', {})
            
            # Check for carousel.standard:store_carousel pattern
            return (item_id.startswith('carousel.standard:store_carousel') and 
                    component.get('id') == 'carousel.standard' and 
                    component.get('category') == 'carousel')
        except:
            return False
            
    def extract_store_carousel_info(self, item):
        """Extract all text information from a store carousel component"""
        try:
            carousel_info = {
                'id': item.get('id', ''),
                'component_id': item.get('component', {}).get('id', ''),
                'component_category': item.get('component', {}).get('category', ''),
                'text_fields': {}
            }
            
            # Extract all text fields
            text_obj = item.get('text', {})
            if isinstance(text_obj, dict):
                for key, value in text_obj.items():
                    if isinstance(value, str) and value.strip():
                        carousel_info['text_fields'][key] = value.strip()
            
            # Only return if we have text fields
            if carousel_info['text_fields']:
                return carousel_info
                
        except Exception as e:
            print(f"Error extracting carousel info: {e}")
            
        return None
        
    def validate_auth_token(self):
        """Validate that authorization token is set"""
        token = self.config.get('AUTHORIZATION_TOKEN', '')
        if not token or token.lower() == 'null' or not token.strip():
            # Show token input dialog
            self.set_auth_token()
            # Re-check after dialog
            token = self.config.get('AUTHORIZATION_TOKEN', '')
            if not token or token.lower() == 'null' or not token.strip():
                raise Exception("Authorization token is required but not set")
                
    def set_auth_token(self):
        """Show dialog to set authorization token"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Authorization Token")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔑 Set Authorization Token", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, text="""🔍 To find your JWT token:

1. Open Charles Proxy and capture DoorDash API requests
2. Look for the 'authorization' header in any request  
3. Copy ONLY the part after 'JWT ' (without the JWT prefix)

Example: authorization: JWT eyJhbGciOiJIUzI1NiJ9...
Copy: eyJhbGciOiJIUzI1NiJ9...

Paste your token below (JWT prefix will be automatically removed):""", 
                               justify=tk.LEFT, wraplength=500)
        instructions.pack(pady=(0, 20))
        
        # Token entry
        token_label = ttk.Label(main_frame, text="Authorization Token:")
        token_label.pack(anchor=tk.W)
        
        token_var = tk.StringVar()
        token_entry = ttk.Entry(main_frame, textvariable=token_var, width=70, font=('Consolas', 10))
        token_entry.pack(fill=tk.X, pady=(5, 20))
        token_entry.focus()
        
        def save_token():
            token = token_var.get().strip()
            if token:
                # Remove JWT prefix if present and clean up
                if token.startswith('JWT '):
                    token = token[4:].strip()
                elif token.startswith('jwt '):
                    token = token[4:].strip()
                
                self.config['AUTHORIZATION_TOKEN'] = token
                
                # Update the GUI variable if it exists
                if 'AUTHORIZATION_TOKEN' in self.config_vars:
                    self.config_vars['AUTHORIZATION_TOKEN'].set(token)
                
                # Update warning banner
                self.update_warning_banner()
                
                dialog.destroy()
                messagebox.showinfo("Token Set", "✅ Authorization token has been set successfully!")
            else:
                messagebox.showerror("Invalid Token", "Please enter a valid authorization token.")
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="💾 Save Token", command=save_token, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Cancel", command=cancel).pack(side=tk.RIGHT)
        
        # Bind Enter key to save
        dialog.bind('<Return>', lambda e: save_token())
        
    def handle_request_error(self, error):
        """Handle errors that occur during the request"""
        error_message = f"❌ Request failed: {str(error)}"
        
        # Clear displays and show error
        self.clear_response()
        self.response_display.insert(tk.END, error_message)
        self.summary_display.insert(tk.END, f"ERROR:\n{error_message}")
        
        # Switch to carousel tab to show error
        self.response_notebook.select(self.carousel_tab)
        
        self.update_status(error_message)
        messagebox.showerror("Request Error", error_message)
        self.is_loading = False
        self.make_request_btn.config(state='normal')
        
    def clear_response(self):
        """Clear all response displays"""
        self.request_display.delete('1.0', tk.END)
        self.response_display.delete('1.0', tk.END)
        self.summary_display.delete('1.0', tk.END)
        self.raw_display.delete('1.0', tk.END)
        self.update_status("Response cleared")
        
    def save_configuration(self):
        """Save configuration changes to memory"""
        try:
            # Update config from GUI variables
            for key, var in self.config_vars.items():
                value = var.get().strip()
                # Handle null values
                if value.lower() == 'null' or value == '':
                    self.config[key] = None if value.lower() == 'null' else ''
                else:
                    self.config[key] = value
            
            # Update warning banner
            self.update_warning_banner()
            
            self.update_status("Configuration saved to memory")
            messagebox.showinfo("Configuration Saved", 
                              "Configuration has been saved to memory.\nUse 'Save to File' to persist changes.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {str(e)}")
            
    def reset_configuration(self):
        """Reset configuration to file values"""
        try:
            # Reload from file
            self.load_config()
            
            # Update GUI variables
            for key, var in self.config_vars.items():
                var.set(self.config.get(key, ''))
            
            self.update_status("Configuration reset to file values")
            messagebox.showinfo("Configuration Reset", "Configuration has been reset to file values.")
        except Exception as e:
            messagebox.showerror("Reset Error", f"Failed to reset configuration: {str(e)}")
            
    def save_to_file(self):
        """Save current configuration to config.env file"""
        try:
            # First save to memory
            self.save_configuration()
            
            # Ask for confirmation
            result = messagebox.askyesno("Save to File", 
                                       "This will overwrite the config.env file with current settings.\n\nProceed?")
            if not result:
                return
                
            config_path = os.path.join(os.path.dirname(__file__), 'config.env')
            
            # Create backup
            backup_path = config_path + '.backup'
            if os.path.exists(config_path):
                import shutil
                shutil.copy2(config_path, backup_path)
            
            # Write new config file
            with open(config_path, 'w') as f:
                f.write("# ============================================================================\n")
                f.write("# DoorDash Realtime Test Configuration\n")
                f.write("# ============================================================================\n")
                f.write("# This file was generated by the GUI configuration editor\n")
                f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Group configurations by category
                categories = {
                    "API Settings": ["API_HOST", "EXPERIENCE_ID", "AUTHORIZATION_TOKEN", "USER_AGENT", "CLIENT_VERSION"],
                    "Session & Headers": ["COOKIE", "SESSION_ID", "CLIENT_REQUEST_ID", "CORRELATION_ID", 
                                        "FACETS_VERSION", "FACETS_FEATURE_STORE", "ACCEPT_LANGUAGE", "USER_LOCALE"],
                    "Location & Context": ["LATITUDE", "LONGITUDE", "SUBMARKET_ID", "DISTRICT_ID", 
                                         "DD_IDS", "DD_LOCATION_CONTEXT"],
                    "Events & Advanced": ["REALTIME_EVENTS", "BFF_ERROR_FORMAT", "SUPPORT_PARTNER_DASHPASS", 
                                        "DEFAULT_VERBOSE", "MAX_VERBOSE_LINES"]
                }
                
                for category, keys in categories.items():
                    f.write(f"# ----------------------\n")
                    f.write(f"# {category}\n")
                    f.write(f"# ----------------------\n\n")
                    
                    for key in keys:
                        if key in self.config:
                            value = self.config[key]
                            if value is None:
                                f.write(f"{key}=null\n")
                            elif isinstance(value, str) and (' ' in value or '"' in value or "'" in value):
                                # Escape quotes and wrap in single quotes
                                escaped_value = value.replace("'", "\\'")
                                f.write(f"{key}='{escaped_value}'\n")
                            else:
                                f.write(f"{key}={value}\n")
                    f.write("\n")
                    
            self.update_status("Configuration saved to config.env")
            messagebox.showinfo("File Saved", 
                              f"Configuration saved to config.env\nBackup created: {os.path.basename(backup_path)}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save to file: {str(e)}")

    def reload_config(self):
        """Reload configuration from file"""
        try:
            self.load_config()
            
            # Update GUI variables if they exist
            if hasattr(self, 'config_vars'):
                for key, var in self.config_vars.items():
                    var.set(self.config.get(key, ''))
            
            # Update warning banner
            self.update_warning_banner()
            
            self.update_status("Configuration reloaded successfully")
            messagebox.showinfo("Config Reloaded", "Configuration has been reloaded from config.env")
        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to reload config: {str(e)}")

    def create_api_host_field_with_presets(self, parent):
        """Create API Host field with presets button"""
        # Base URL field
        base_url_frame = ttk.Frame(parent)
        base_url_frame.pack(fill=tk.X, pady=2)
        
        label_widget = ttk.Label(base_url_frame, text="Base URL:", font=('Arial', 9, 'bold'), width=20)
        label_widget.pack(side=tk.LEFT, padx=(0, 10))
        
        initial_value = self.config.get('API_BASE_URL', 'https://unified-gateway.doordash.com')
        var = tk.StringVar(value=initial_value)
        self.config_vars['API_BASE_URL'] = var
        
        entry = ttk.Entry(base_url_frame, textvariable=var, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        desc_label = ttk.Label(base_url_frame, text="e.g., https://consumer-mobile-bff.doordash.com", 
                             font=('Arial', 8), foreground='gray')
        desc_label.pack(side=tk.RIGHT)
        
        # Endpoint Path field
        endpoint_frame = ttk.Frame(parent)
        endpoint_frame.pack(fill=tk.X, pady=2)
        
        label_widget2 = ttk.Label(endpoint_frame, text="Endpoint Path:", font=('Arial', 9, 'bold'), width=20)
        label_widget2.pack(side=tk.LEFT, padx=(0, 10))
        
        initial_path = self.config.get('API_ENDPOINT_PATH', '/cx/v3/feed/realtime_recommendation')
        path_var = tk.StringVar(value=initial_path)
        self.config_vars['API_ENDPOINT_PATH'] = path_var
        
        entry2 = ttk.Entry(endpoint_frame, textvariable=path_var, width=50)
        entry2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Presets button
        ttk.Button(endpoint_frame, text="🔧 API Presets", command=self.open_api_presets_modal).pack(side=tk.LEFT)
        
        desc_label2 = ttk.Label(endpoint_frame, text="e.g., /v3/feed/homepage", 
                              font=('Arial', 8), foreground='gray')
        desc_label2.pack(side=tk.RIGHT)
        
    def open_api_presets_modal(self):
        """Open API presets modal with dropdown selector"""
        preset_dialog = tk.Toplevel(self.root)
        preset_dialog.title("API Configuration Presets")
        preset_dialog.geometry("600x400")
        preset_dialog.transient(self.root)
        preset_dialog.grab_set()
        
        # Center the dialog
        preset_dialog.update_idletasks()
        x = (preset_dialog.winfo_screenwidth() // 2) - (300)
        y = (preset_dialog.winfo_screenheight() // 2) - (200)
        preset_dialog.geometry(f"600x400+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(preset_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔧 API Configuration Presets", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Select a preset configuration to quickly set up API endpoints with all required headers and parameters.",
                              font=('Arial', 10), wraplength=550, justify=tk.CENTER)
        desc_label.pack(pady=(0, 30))
        
        # Preset selector frame
        selector_frame = ttk.LabelFrame(main_frame, text="Select Preset Configuration", padding=15)
        selector_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Dropdown with presets
        preset_label = ttk.Label(selector_frame, text="Available Presets:", font=('Arial', 11, 'bold'))
        preset_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Define preset options
        self.preset_options = {
            "🎯 Unified Gateway - Realtime Recommendation": {
                "description": "Current realtime recommendation endpoint with pagination support",
                "endpoint": "unified-gateway.doordash.com/cx/v3/feed/realtime_recommendation",
                "method": self.apply_unified_realtime_preset
            },
            "🏠 Consumer Mobile BFF - Homepage": {
                "description": "Homepage feed endpoint with cursor pagination and full feature flags",
                "endpoint": "consumer-mobile-bff.doordash.com/v3/feed/homepage",
                "method": self.apply_homepage_preset
            },
            "📱 DoorDash Prod App": {
                "description": "Production Android app configuration with latest device IDs and session data",
                "endpoint": "consumer-mobile-bff.doordash.com/v3/feed/homepage",
                "method": self.apply_prod_app_preset
            },
            "📱 Consumer Mobile BFF - Feed Me (Legacy)": {
                "description": "Legacy feed me endpoint with iOS feature flags",
                "endpoint": "consumer-mobile-bff.doordash.com/v3/feed/me",
                "method": self.apply_feed_me_preset
            }
        }
        
        # Dropdown combobox
        self.selected_preset = tk.StringVar()
        preset_combo = ttk.Combobox(selector_frame, textvariable=self.selected_preset, 
                                   values=list(self.preset_options.keys()),
                                   state="readonly", width=70, font=('Arial', 10))
        preset_combo.pack(fill=tk.X, pady=(0, 15))
        preset_combo.set("Select a preset...")
        
        # Description area
        desc_frame = ttk.Frame(selector_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(desc_frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.preset_desc_label = ttk.Label(desc_frame, text="Choose a preset to see its description", 
                                          font=('Arial', 9), wraplength=500, justify=tk.LEFT)
        self.preset_desc_label.pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Label(desc_frame, text="Endpoint:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        self.preset_endpoint_label = ttk.Label(desc_frame, text="", 
                                              font=('Consolas', 9), foreground='blue')
        self.preset_endpoint_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Update description when selection changes
        def on_preset_selected(event):
            selected = self.selected_preset.get()
            if selected in self.preset_options:
                preset_info = self.preset_options[selected]
                self.preset_desc_label.config(text=preset_info["description"])
                self.preset_endpoint_label.config(text=preset_info["endpoint"])
            else:
                self.preset_desc_label.config(text="Choose a preset to see its description")
                self.preset_endpoint_label.config(text="")
        
        preset_combo.bind('<<ComboboxSelected>>', on_preset_selected)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        def apply_selected_preset():
            selected = self.selected_preset.get()
            if selected in self.preset_options:
                preset_info = self.preset_options[selected]
                preset_info["method"]()  # Call the preset method
            else:
                messagebox.showwarning("No Selection", "Please select a preset configuration first.")
        
        # Apply and Cancel buttons
        ttk.Button(buttons_frame, text="✅ Apply Preset", command=apply_selected_preset,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(buttons_frame, text="❌ Cancel", command=preset_dialog.destroy).pack(side=tk.RIGHT)

    def apply_feed_me_preset(self):
        """Apply the Feed Me preset configuration based on the provided curl command"""
        # Configuration based on the curl command provided
        feed_me_config = {
            'API_BASE_URL': 'https://consumer-mobile-bff.doordash.com',
            'API_ENDPOINT_PATH': '/v3/feed/me',
            'EXPERIENCE_ID': 'doordash',
            'USER_AGENT': 'DoordashConsumer/7.32.0 (iPhone; iOS 18.5; Scale/3.0)',
            'CLIENT_VERSION': 'ios v7.32.0 b309062.250806',
            'ACCEPT_LANGUAGE': 'en-US',
            'USER_LOCALE': 'en-US',
            'LATITUDE': '34.0282903',
            'LONGITUDE': '-118.373421',
            'SUBMARKET_ID': '1',
            'DISTRICT_ID': '3',
            'FACETS_VERSION': '6.0.0',
            'FACETS_FEATURE_STORE': 'treatmentVariant3',
            'BFF_ERROR_FORMAT': 'v2',
            'SUPPORT_PARTNER_DASHPASS': 'true',
            'SESSION_ID': '7DCCF941-573F-4DB5-BABF-4DD06ADFC539-cx-ios',
            'CLIENT_REQUEST_ID': '0D4ED886-7FD9-47BA-BBD7-A31C9127B600-cx-ios',
            'CORRELATION_ID': 'FE22D422-E4BC-4040-94EB-096986CEAB16-cx-ios',
            'DD_LOCATION_CONTEXT': 'eyJhZGRyZXNzX2lkIjoiMzQ1MjMzNDI5IiwiY2l0eSI6IkxvcyBBbmdlbGVzIiwiY29uc3VtZXJfYWRkcmVzc19saW5rX2lkIjoiMTQ1NTEyMzQxMiIsImNvdW50cnlfc2hvcnRfbmFtZSI6IlVTIiwiZGlzdHJpY3RfaWQiOiIzIiwiaXNfZ3Vlc3RfY29uc3VtZXIiOmZhbHNlLCJsYXQiOjM0LjAyODI5MDMsImxuZyI6LTExOC4zNzM0MjEsIm1hcmtldF9pZCI6IjIiLCJzdGF0ZSI6IkNBIiwic3VibWFya2V0X2lkIjoiMSIsInRpbWV6b25lIjoiQW1lcmljYVwvTG9zX0FuZ2VsZXMiLCJ6aXBjb2RlIjoiOTAwMTYifQ==',
            'DD_IDS': '{"dd_ios_idfv_id":"175409C4-E708-4493-B972-48EFE9668407","dd_ios_idfa_id":"00000000-0000-0000-0000-000000000000","dd_login_id":"lx_5451FB95-9C62-407B-9484-EA771FB317E2","dd_device_id":"dx_175409C4-E708-4493-B972-48EFE9668407","dd_delivery_correlation_id":"d63366d8-ae15-4820-ac43-d570b318dc98","dd_session_id":"sx_71A0763A-EB00-4FEE-A3E1-DE1C15F69892"}',
            'COOKIE': 'dd_session_id=sx_71A0763A-EB00-4FEE-A3E1-DE1C15F69892; dd_request_id=0D4ED886-7FD9-47BA-BBD7-A31C9127B600-cx-ios',
            'REALTIME_EVENTS': '[]',  # Feed Me doesn't use realtime events
            'DEFAULT_VERBOSE': 'true',
            'MAX_VERBOSE_LINES': '100'
        }
        
        # Update config dictionary
        for key, value in feed_me_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in feed_me_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        # Close the preset dialog
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
                break
        
        self.update_warning_banner()
        self.update_status("Applied Feed Me preset configuration")
        messagebox.showinfo("Preset Applied", 
                          "Feed Me preset configuration applied!\n\n"
                          "⚠️ Note: You still need to set your Authorization Token\n"
                          "The preset has configured all other required headers and parameters.")
    
    def apply_unified_realtime_preset(self):
        """Apply the Unified Gateway - Realtime Recommendation preset configuration"""
        # Configuration based on the first curl command provided
        unified_realtime_config = {
            'API_BASE_URL': 'https://unified-gateway.doordash.com',
            'API_ENDPOINT_PATH': '/cx/v3/feed/realtime_recommendation',
            'EXPERIENCE_ID': 'doordash',
            'USER_AGENT': 'DoorDashConsumer/Android 16.0.0-prod-debug',
            'CLIENT_VERSION': 'android v16.0.0-prod-debug b16000009',
            'ACCEPT_LANGUAGE': 'en-US',
            'USER_LOCALE': 'en-US',
            'LATITUDE': '34.0282903',
            'LONGITUDE': '-118.373421',
            'SUBMARKET_ID': '1',
            'DISTRICT_ID': '3',
            'FACETS_VERSION': '4.0.0',
            'FACETS_FEATURE_STORE': 'treatmentVariant3',
            'BFF_ERROR_FORMAT': 'v2',
            'SUPPORT_PARTNER_DASHPASS': 'true',
            'SESSION_ID': '88d4f03e-14d2-44bb-a1e0-084db5d7bd0f-dd-and',
            'CLIENT_REQUEST_ID': '0b7956f5-3b04-4fcc-bf13-5f83916d5ad7-dd-and',
            'CORRELATION_ID': '348fce35-5953-415e-a0bf-02394a8a6cd7-dd-and',
            'DD_LOCATION_CONTEXT': 'eyJsYXQiOjM0LjAyODI5MDMsImxuZyI6LTExOC4zNzM0MjEsIm1hcmtldF9pZCI6IjIiLCJzdWJtYXJrZXRfaWQiOiIxIiwiZGlzdHJpY3RfaWQiOiIzIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiemlwY29kZSI6IjkwMDE2IiwiY291bnRyeV9zaG9ydF9uYW1lIjoiVVMiLCJjaXR5IjoiTG9zIEFuZ2VsZXMiLCJzdGF0ZSI6IkNBIiwiY29uc3VtZXJfYWRkcmVzc19saW5rX2lkIjoiMTQ1NTEyMzQxMiIsImFkZHJlc3NfaWQiOiIzNDUyMzM0MjkiLCJpc19ndWVzdF9jb25zdW1lciI6ZmFsc2V9',
            'DD_IDS': '{"dd_device_id":"78158b794698adba","dd_delivery_correlation_id":"6823d337-a3cf-4072-81b3-aa6fcba69b8d","dd_login_id":"lx_d16f81d2-773c-4f06-9997-b0de82bfbf32","dd_session_id":"sx_eb41331c-72f7-4b26-bba4-1e58f7ba6566","dd_android_id":"78158b794698adba","dd_android_advertising_id":"29804a87-b1f8-4db9-be15-a25ec4606c91"}',
            'COOKIE': '__cf_bm=DIupgxWsFkASAiujjiTT2MT3ur4TChDFCiT_wEhxM0k-1754597899-1.0.1.1-Pq13lqhelrTdfq3KP0bH2WIPROBGaoqZ4xsLnORM14sHGeP9WeNJHYnioQCpI9RUr1tAssqTfXIGS8NNIE1Zv_QpGiGnSPGrHkh86fGk3qc; dd_country_shortname=US; dd_market_id=2',
            'REALTIME_EVENTS': '[{"action_type":"store_visit","entity_id":"4932","timestamp":"2025-08-07 12:47:57"}]',
            'DEFAULT_VERBOSE': 'true',
            'MAX_VERBOSE_LINES': '100'
        }
        
        # Update config dictionary
        for key, value in unified_realtime_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in unified_realtime_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        # Close the preset dialog
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
                break
        
        self.update_warning_banner()
        self.update_status("Applied Unified Gateway - Realtime Recommendation preset configuration")
        messagebox.showinfo("Preset Applied", 
                          "Unified Gateway - Realtime Recommendation preset applied!\n\n"
                          "⚠️ Note: You still need to set your Authorization Token\n"
                          "The preset has configured all other required headers and parameters.")
    
    def apply_homepage_preset(self):
        """Apply the Consumer Mobile BFF - Homepage preset configuration"""
        # Configuration based on the homepage curl command provided
        homepage_config = {
            'API_BASE_URL': 'https://consumer-mobile-bff.doordash.com',
            'API_ENDPOINT_PATH': '/v3/feed/homepage',
            'EXPERIENCE_ID': 'doordash',
            'USER_AGENT': 'DoorDashConsumer/Android 16.0.0-prod-debug',
            'CLIENT_VERSION': 'android v16.0.0-prod-debug b16000009',
            'ACCEPT_LANGUAGE': 'en-US',
            'USER_LOCALE': 'en-US',
            'LATITUDE': '34.0282903',
            'LONGITUDE': '-118.373421',
            'SUBMARKET_ID': '1',
            'DISTRICT_ID': '3',
            'FACETS_VERSION': '4.0.0',
            'FACETS_FEATURE_STORE': 'treatmentVariant3',
            'BFF_ERROR_FORMAT': 'v2',
            'SUPPORT_PARTNER_DASHPASS': 'true',
            'SESSION_ID': '88d4f03e-14d2-44bb-a1e0-084db5d7bd0f-dd-and',
            'CLIENT_REQUEST_ID': '0b7956f5-3b04-4fcc-bf13-5f83916d5ad7-dd-and',
            'CORRELATION_ID': '348fce35-5953-415e-a0bf-02394a8a6cd7-dd-and',
            'DD_LOCATION_CONTEXT': 'eyJsYXQiOjM0LjAyODI5MDMsImxuZyI6LTExOC4zNzM0MjEsIm1hcmtldF9pZCI6IjIiLCJzdWJtYXJrZXRfaWQiOiIxIiwiZGlzdHJpY3RfaWQiOiIzIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiemlwY29kZSI6IjkwMDE2IiwiY291bnRyeV9zaG9ydF9uYW1lIjoiVVMiLCJjaXR5IjoiTG9zIEFuZ2VsZXMiLCJzdGF0ZSI6IkNBIiwiY29uc3VtZXJfYWRkcmVzc19saW5rX2lkIjoiMTQ1NTEyMzQxMiIsImFkZHJlc3NfaWQiOiIzNDUyMzM0MjkiLCJpc19ndWVzdF9jb25zdW1lciI6ZmFsc2V9',
            'DD_IDS': '{"dd_device_id":"78158b794698adba","dd_delivery_correlation_id":"6823d337-a3cf-4072-81b3-aa6fcba69b8d","dd_login_id":"lx_d16f81d2-773c-4f06-9997-b0de82bfbf32","dd_session_id":"sx_eb41331c-72f7-4b26-bba4-1e58f7ba6566","dd_android_id":"78158b794698adba","dd_android_advertising_id":"29804a87-b1f8-4db9-be15-a25ec4606c91"}',
            'COOKIE': '__cf_bm=DIupgxWsFkASAiujjiTT2MT3ur4TChDFCiT_wEhxM0k-1754597899-1.0.1.1-Pq13lqhelrTdfq3KP0bH2WIPROBGaoqZ4xsLnORM14sHGeP9WeNJHYnioQCpI9RUr1tAssqTfXIGS8NNIE1Zv_QpGiGnSPGrHkh86fGk3qc; dd_country_shortname=US; dd_market_id=2',
            'REALTIME_EVENTS': '[{"action_type":"store_visit","entity_id":"4932","timestamp":"2025-08-07 12:47:57"}] cursor=eyJvZmZzZXQiOjAsImNvbnRlbnRfaWRzIjpbXSwicmVxdWVzdF9wYXJlbnRfaWQiOiIiLCJyZXF1ZXN0X2NoaWxkX2lkIjoiIiwicmVxdWVzdF9jaGlsZF9jb21wb25lbnRfaWQiOiIiLCJjcm9zc192ZXJ0aWNhbF9wYWdlX3R5cGUiOiJIT01FUEFHRSIsInBhZ2Vfc3RhY2tfdHJhY2UiOltdLCJ2ZXJ0aWNhbF9pZHMiOlsxMDMsMywyLDE3NCwzNywxMzksMTQ2LDEzNiw3MCwyNjgsMjQxLDIzNSwyMzYsMTEwMDAxLDQsMjM4LDI0MywyODIsMTEwMDE2LDEwMDMzM10sInZlcnRpY2FsX2NvbnRleHRfaWQiOm51bGwsImxheW91dF9vdmVycmlkZSI6IlVOU1BFQ0lGSUVEIiwic2luZ2xlX3N0b3JlX2lkIjpudWxsLCJzZWFyY2hfaXRlbV9jYXJvdXNlbF9jdXJzb3IiOm51bGwsImNhdGVnb3J5X2lkcyI6W10sImNvbGxlY3Rpb25faWRzIjpbXSwiZGRfcGxhY2VfaWRzIjpbImMyNjc5NjAzLTg4OGYtNDI0NC1iZTcxLTYzZDc5NmU4MGNiMCIsImQxYzRhZjBjLTJmNzMtNDljNC05YzkzLWM1OWE4YzMwODcyNSJdLCJuZXh0X3BhZ2VfY2FjaGVfa2V5IjoiVkVSVElDQUw6MTk1NDQyMDg1Ojc4MTU4Yjc5NDY5OGFkYmE6MTplN2E1YTAzMy1hZTA4LTQyY2MtODdjYi1iYzUxODM0MThmYTM6TFo0IiwiaXNfcGFnaW5hdGlvbl9mYWxsYmFjayI6bnVsbCwic291cmNlX3BhZ2VfdHlwZSI6bnVsbCwiZ2VvX3R5cGUiOiIiLCJnZW9faWQiOiIiLCJrZXl3b3JkIjoiIiwiYWRzX2N1cnNvcl9jYWNoZV9rZXkiOm51bGwsInZpc3VhbF9haXNsZXNfaW5zZXJ0aW9uX2luZGV4IjpudWxsLCJiYXNlQ3Vyc29yIjp7InBhZ2VfaWQiOiIiLCJwYWdlX3R5cGUiOiJOT1RfQVBQTElDQUJMRSIsImN1cnNvcl92ZXJzaW9uIjoiRkFDRVQifSwidmVydGljYWxfbmFtZXMiOnt9LCJpdGVtX2lkcyI6W10sIm1lcmNoYW50X3N1cHBsaWVkX2lkcyI6W10sImlzX291dF9vZl9zdG9jayI6bnVsbCwibWVudV9pZCI6bnVsbCwidHJhY2tpbmciOm51bGwsImRpZXRhcnlfdGFnIjpudWxsLCJvcmlnaW5fdGl0bGUiOm51bGwsInJhbmtlZF9yZW1haW5pbmdfY29sbGVjdGlvbl9pZHMiOm51bGwsInByZXZpb3VzbHlfc2Vlbl9jb2xsZWN0aW9uX2lkcyI6W10sInByZWNoZWNrb3V0X2J1bmRsZV9zZWFyY2hfaW5mbyI6bnVsbCwidG90YWxfaXRlbXNfb2Zmc2V0IjowLCJ0b3RhbF9hZHNfcHJldmlvdXNseV9ibGVuZGVkIjowLCJ2ZXJ0aWNhbF90aXRsZSI6bnVsbCwibXVsdGlfc3RvcmVfZW50aXRpZXMiOltdLCJjdXJzb3JWZXJzaW9uIjoiRkFDRVRfQ09OVEVOVF9PRkZTRVQiLCJwYWdlSWQiOiIiLCJwYWdlVHlwZSI6Ik5PVF9BUFBMSUNBQkxFIn0%3D',
            'DEFAULT_VERBOSE': 'true',
            'MAX_VERBOSE_LINES': '100'
        }
        
        # Update config dictionary
        for key, value in homepage_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in homepage_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        # Close the preset dialog
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
                break
        
        self.update_warning_banner()
        self.update_status("Applied Consumer Mobile BFF - Homepage preset configuration")
        messagebox.showinfo("Preset Applied", 
                          "Consumer Mobile BFF - Homepage preset applied!\n\n"
                          "⚠️ Note: You still need to set your Authorization Token\n"
                          "The preset has configured all other required headers and parameters including cursor.")
    
    def apply_prod_app_preset(self):
        """Apply the DoorDash Prod App preset configuration"""
        # Configuration based on the production Android app curl command provided
        prod_app_config = {
            'API_BASE_URL': 'https://consumer-mobile-bff.doordash.com',
            'API_ENDPOINT_PATH': '/v3/feed/homepage',
            'EXPERIENCE_ID': 'doordash',
            'USER_AGENT': 'DoorDashConsumer/Android 15.214.6',
            'CLIENT_VERSION': 'android v15.214.6',
            'ACCEPT_LANGUAGE': 'en-US',
            'USER_LOCALE': 'en-US',
            'LATITUDE': '34.0282903',
            'LONGITUDE': '-118.373421',
            'SUBMARKET_ID': '1',
            'DISTRICT_ID': '3',
            'FACETS_VERSION': '4.0.0',
            'FACETS_FEATURE_STORE': 'treatmentVariant3',
            'BFF_ERROR_FORMAT': 'v2',
            'SUPPORT_PARTNER_DASHPASS': 'true',
            'SESSION_ID': '6703ac28-37e9-406c-a4d2-f7467a2bab19-dd-and',
            'CLIENT_REQUEST_ID': '4fb49653-4bd4-40b7-b2bd-7bf87a2a4885-dd-and',
            'CORRELATION_ID': '3f28aa97-e023-43ec-aace-a17500a8e20f-dd-and',
            'DD_LOCATION_CONTEXT': 'eyJsYXQiOjM0LjAyODI5MDMsImxuZyI6LTExOC4zNzM0MjEsIm1hcmtldF9pZCI6IjIiLCJzdWJtYXJrZXRfaWQiOiIxIiwiZGlzdHJpY3RfaWQiOiIzIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiemlwY29kZSI6IjkwMDE2IiwiY291bnRyeV9zaG9ydF9uYW1lIjoiVVMiLCJjaXR5IjoiTG9zIEFuZ2VsZXMiLCJzdGF0ZSI6IkNBIiwiY29uc3VtZXJfYWRkcmVzc19saW5rX2lkIjoiMTQ1NTEyMzQxMiIsImFkZHJlc3NfaWQiOiIzNDUyMzM0MjkiLCJpc19ndWVzdF9jb25zdW1lciI6ZmFsc2V9',
            'DD_IDS': '{"dd_device_id":"1211c7331d5ffe2f","dd_delivery_correlation_id":"76b077ad-71fb-47e8-8ce9-9b59008f841a","dd_login_id":"lx_f5ccdfd4-f9b5-402c-afee-e9386976fa76","dd_session_id":"sx_9eceac3d-2f25-4be3-b2cb-46d5a1b0aa3f","dd_android_id":"1211c7331d5ffe2f","dd_android_advertising_id":"5136cf26-f0fd-43fd-8bc5-4e96847df333"}',
            'COOKIE': '',  # No cookie in the provided curl command
            'REALTIME_EVENTS': '[] cursor=eyJvZmZzZXQiOjAsImNvbnRlbnRfaWRzIjpbXSwicmVxdWVzdF9wYXJlbnRfaWQiOiIiLCJyZXF1ZXN0X2NoaWxkX2lkIjoiIiwicmVxdWVzdF9jaGlsZF9jb21wb25lbnRfaWQiOiIiLCJjcm9zc192ZXJ0aWNhbF9wYWdlX3R5cGUiOiJIT01FUEFHRSIsInBhZ2Vfc3RhY2tfdHJhY2UiOltdLCJ2ZXJ0aWNhbF9pZHMiOlsxMDMsMywyLDE3NCwzNywxMzksMTQ2LDEzNiw3MCwyNjgsMjQxLDIzNSwyMzYsMTEwMDAxLDQsMjM4LDI0MywyODIsMTEwMDE2LDEwMDMzM10sInZlcnRpY2FsX2NvbnRleHRfaWQiOm51bGwsImxheW91dF9vdmVycmlkZSI6IlVOU1BFQ0lGSUVEIiwic2luZ2xlX3N0b3JlX2lkIjpudWxsLCJzZWFyY2hfaXRlbV9jYXJvdXNlbF9jdXJzb3IiOm51bGwsImNhdGVnb3J5X2lkcyI6W10sImNvbGxlY3Rpb25faWRzIjpbXSwiZGRfcGxhY2VfaWRzIjpbImMyNjc5NjAzLTg4OGYtNDI0NC1iZTcxLTYzZDc5NmU4MGNiMCIsImQxYzRhZjBjLTJmNzMtNDljNC05YzkzLWM1OWE4YzMwODcyNSJdLCJuZXh0X3BhZ2VfY2FjaGVfa2V5IjoiVkVSVElDQUw6MTk1NDQyMDg1OjEyMTFjNzMzMWQ1ZmZlMmY6MTo4MGZkNWFmMS0yOGZlLTQ3YzctYjljNS0zZTE2MGU1OGRhMmY6TFo0IiwiaXNfcGFnaW5hdGlvbl9mYWxsYmFjayI6bnVsbCwic291cmNlX3BhZ2VfdHlwZSI6bnVsbCwiZ2VvX3R5cGUiOiIiLCJnZW9faWQiOiIiLCJrZXl3b3JkIjoiIiwiYWRzX2N1cnNvcl9jYWNoZV9rZXkiOm51bGwsInZpc3VhbF9haXNsZXNfaW5zZXJ0aW9uX2luZGV4IjpudWxsLCJiYXNlQ3Vyc29yIjp7InBhZ2VfaWQiOiIiLCJwYWdlX3R5cGUiOiJOT1RfQVBQTElDQUJMRSIsImN1cnNvcl92ZXJzaW9uIjoiRkFDRVQifSwidmVydGljYWxfbmFtZXMiOnt9LCJpdGVtX2lkcyI6W10sIm1lcmNoYW50X3N1cHBsaWVkX2lkcyI6W10sImlzX291dF9vZl9zdG9jayI6bnVsbCwibWVudV9pZCI6bnVsbCwidHJhY2tpbmciOm51bGwsImRpZXRhcnlfdGFnIjpudWxsLCJvcmlnaW5fdGl0bGUiOm51bGwsInJhbmtlZF9yZW1haW5pbmdfY29sbGVjdGlvbl9pZHMiOm51bGwsInByZXZpb3VzbHlfc2Vlbl9jb2xsZWN0aW9uX2lkcyI6W10sInByZWNoZWNrb3V0X2J1bmRsZV9zZWFyY2hfaW5mbyI6bnVsbCwidG90YWxfaXRlbXNfb2Zmc2V0IjowLCJ0b3RhbF9hZHNfcHJldmlvdXNseV9ibGVuZGVkIjowLCJ2ZXJ0aWNhbF90aXRsZSI6bnVsbCwibXVsdGlfc3RvcmVfZW50aXRpZXMiOltdLCJjdXJzb3JWZXJzaW9uIjoiRkFDRVRfQ09OVEVOVF9PRkZTRVQiLCJwYWdlSWQiOiIiLCJwYWdlVHlwZSI6Ik5PVF9BUFBMSUNBQkxFIn0=',
            'DEFAULT_VERBOSE': 'true',
            'MAX_VERBOSE_LINES': '100'
        }
        
        # Update config dictionary
        for key, value in prod_app_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in prod_app_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        # Close the preset dialog
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
                break
        
        self.update_warning_banner()
        self.update_status("Applied DoorDash Prod App preset configuration")
        messagebox.showinfo("Preset Applied", 
                          "DoorDash Prod App preset applied!\n\n"
                          "⚠️ Note: You still need to set your Authorization Token\n"
                          "This preset includes production Android device IDs and latest session data.")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run the application
    app = DoorDashAPIGUI(root)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main() 