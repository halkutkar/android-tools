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
        
        # Response section
        self.create_response_section(main_frame)
        
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
        if not self.config.get('API_HOST'):
            warnings.append("⚠️ API Host not configured")
            
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
        """Create request controls section"""
        controls_frame = ttk.LabelFrame(parent, text="🎯 Request Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Options frame
        options_frame = ttk.Frame(controls_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Verbose mode checkbox
        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Show detailed response", 
                       variable=self.verbose_var).pack(side=tk.LEFT)
        
        # Auto-parse checkbox
        self.auto_parse_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-parse carousel titles", 
                       variable=self.auto_parse_var).pack(side=tk.LEFT, padx=(20, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Make Request button
        self.request_button = ttk.Button(buttons_frame, text="🚀 Make API Request", 
                                       command=self.make_request_threaded,
                                       style='Accent.TButton')
        self.request_button.pack(side=tk.LEFT)
        
        # Clear button
        ttk.Button(buttons_frame, text="🗑️ Clear Response", 
                  command=self.clear_response).pack(side=tk.LEFT, padx=(10, 0))
        
        # Reload config button
        ttk.Button(buttons_frame, text="🔄 Reload from File", 
                  command=self.reload_config).pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(buttons_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
        
    def create_response_section(self, parent):
        """Create response display section"""
        response_frame = ttk.LabelFrame(parent, text="📊 API Response", padding=10)
        response_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(response_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="📈 Summary")
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, height=10, 
                                                     font=('Monaco', 10))
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Raw response tab
        self.raw_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.raw_frame, text="📋 Raw Response")
        
        self.raw_text = scrolledtext.ScrolledText(self.raw_frame, height=10, 
                                                 font=('Monaco', 9))
        self.raw_text.pack(fill=tk.BOTH, expand=True)
        
        # Carousel titles tab
        self.carousel_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.carousel_frame, text="🎠 Carousel Titles")
        
        self.carousel_text = scrolledtext.ScrolledText(self.carousel_frame, height=10, 
                                                      font=('Arial', 10))
        self.carousel_text.pack(fill=tk.BOTH, expand=True)
        
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
        """Validate that auth token is set"""
        if not self.config.get('AUTHORIZATION_TOKEN'):
            result = messagebox.askyesno(
                "Authorization Token Required", 
                "Authorization token is not set. Would you like to set it now?"
            )
            if result:
                return self.set_auth_token()
            else:
                return False
        return True
        
    def set_auth_token(self):
        """Open dialog to set authorization token"""
        token_dialog = tk.Toplevel(self.root)
        token_dialog.title("Set Authorization Token")
        token_dialog.geometry("520x320")
        token_dialog.transient(self.root)
        token_dialog.grab_set()
        
        # Center the dialog
        token_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(token_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="🔑 Enter JWT Authorization Token:", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Context instructions
        context_text = ("To find your JWT token:\n"
                       "1. Open Charles Proxy and capture DoorDash API requests\n"
                       "2. Look for the 'authorization' header in any request\n"
                       "3. Copy ONLY the part after 'JWT ' (without the JWT prefix)\n\n"
                       "Example: authorization: JWT eyJhbGciOiJIUzI1NiJ9...\n"
                       "Copy: eyJhbGciOiJIUzI1NiJ9...")
        
        ttk.Label(main_frame, text=context_text, 
                 font=('Arial', 9), wraplength=450, justify=tk.LEFT).pack(pady=(0, 15))
        
        # Token entry
        token_var = tk.StringVar()
        token_entry = ttk.Entry(main_frame, textvariable=token_var, width=60)
        token_entry.pack(pady=(0, 20), fill=tk.X)
        token_entry.focus()
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        def save_token():
            token = token_var.get().strip()
            if token:
                # Remove JWT prefix if present
                if token.startswith('JWT '):
                    token = token[4:].strip()
                
                self.config['AUTHORIZATION_TOKEN'] = token
                self.update_status("Authorization token updated successfully")
                self.refresh_config_display()
                self.update_warning_banner()  # Update warning banner
                token_dialog.destroy()
                messagebox.showinfo("Success", "Authorization token has been set successfully!")
                return True
            else:
                messagebox.showerror("Error", "Please enter a valid token")
                return False
                
        def cancel():
            token_dialog.destroy()
            return False
            
        ttk.Button(buttons_frame, text="✅ Save Token", command=save_token).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="❌ Cancel", command=cancel).pack(side=tk.LEFT, padx=(10, 0))
        
        # Bind Enter key to save
        token_entry.bind('<Return>', lambda e: save_token())
        
        # Wait for dialog to close
        token_dialog.wait_window()
        return self.config.get('AUTHORIZATION_TOKEN') is not None
        
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
        
        self.create_config_field(scrollable_frame, "API Host", "API_HOST", 
                               "DoorDash API hostname")
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
        if not self.validate_auth_token():
            return
            
        self.is_loading = True
        self.request_button.config(state='disabled')
        self.progress.start()
        
        thread = threading.Thread(target=self.make_request)
        thread.daemon = True
        thread.start()
        
    def make_request(self):
        """Make the actual API request"""
        try:
            self.update_status("Preparing API request...")
            
            # Save current GUI configuration to memory first
            if hasattr(self, 'config_vars'):
                for key, var in self.config_vars.items():
                    value = var.get().strip()
                    if value.lower() == 'null' or value == '':
                        self.config[key] = None if value.lower() == 'null' else ''
                    else:
                        self.config[key] = value
            
            # Prepare headers
            headers = {
                "Host": self.config.get("API_HOST", ""),
                "Cookie": self.config.get("COOKIE", ""),
                "x-facets-version": self.config.get("FACETS_VERSION", ""),
                "x-facets-feature-store-cell-redesign-round-3": self.config.get("FACETS_FEATURE_STORE", ""),
                "x-realtime-recommendation-events": self.config.get("REALTIME_EVENTS", ""),
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
                "dd-location-context": self.config.get("DD_LOCATION_CONTEXT", "")
            }
            
            # Prepare URL with query parameters
            url = f"https://{self.config.get('API_HOST', '')}/cx/v3/feed/realtime_recommendation"
            params = {
                "common_fields.lat": self.config.get("LATITUDE", ""),
                "common_fields.lng": self.config.get("LONGITUDE", ""),
                "common_fields.submarket_id": self.config.get("SUBMARKET_ID", ""),
                "common_fields.district_id": self.config.get("DISTRICT_ID", "")
            }
            
            self.update_status("Making API request...")
            
            # Make the request
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # Process response
            self.root.after(0, self.process_response, response)
            
        except Exception as e:
            self.root.after(0, self.handle_error, str(e))
            
    def process_response(self, response):
        """Process and display the API response"""
        try:
            self.update_status(f"Processing response (Status: {response.status_code})...")
            
            # Clear previous content
            self.clear_response()
            
            # Display summary
            summary = self.create_summary(response)
            self.summary_text.insert(tk.END, summary)
            
            # Display raw response if verbose mode
            if self.verbose_var.get():
                try:
                    formatted_json = json.dumps(response.json(), indent=2)
                    self.raw_text.insert(tk.END, formatted_json)
                except:
                    self.raw_text.insert(tk.END, response.text)
            else:
                self.raw_text.insert(tk.END, "Enable 'Show detailed response' to see raw data")
                
            # Parse and display carousel titles
            if self.auto_parse_var.get():
                carousels = self.extract_carousel_titles(response)
                self.display_carousels(carousels)
                
            self.update_status(f"Request completed successfully (Status: {response.status_code})")
            
        except Exception as e:
            self.handle_error(f"Error processing response: {str(e)}")
        finally:
            self.is_loading = False
            self.request_button.config(state='normal')
            self.progress.stop()
            
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
            except:
                pass
        else:
            summary += f"❌ Request Status: FAILED\n"
            
        summary += f"\n{'='*50}\n"
        return summary
        
    def extract_carousel_titles(self, response):
        """Extract carousel titles from specific carousel components only"""
        carousels = []
        try:
            if response.status_code == 200:
                # Try JSON parsing first
                try:
                    data = response.json()
                    carousels = self.find_specific_carousel_titles(data)
                except:
                    # Fall back to regex search for specific carousel pattern
                    text = response.text
                    carousels = self.extract_carousel_titles_regex(text)
        except Exception as e:
            carousels = [f"Error extracting carousels: {str(e)}"]
            
        return carousels
        
    def find_specific_carousel_titles(self, data, carousels=None):
        """Find titles specifically from carousel.standard components"""
        if carousels is None:
            carousels = []
            
        if isinstance(data, dict):
            # Check if this is a carousel component we're interested in
            if self.is_target_carousel(data):
                title = self.extract_title_from_carousel(data)
                if title and title not in carousels:
                    carousels.append(title)
            
            # Recursively search through all values
            for value in data.values():
                self.find_specific_carousel_titles(value, carousels)
                
        elif isinstance(data, list):
            for item in data:
                self.find_specific_carousel_titles(item, carousels)
                
        return carousels
        
    def is_target_carousel(self, item):
        """Check if item is a target carousel component"""
        if not isinstance(item, dict):
            return False
            
        # Check for carousel.standard component
        component = item.get('component', {})
        if not isinstance(component, dict):
            return False
            
        component_id = component.get('id', '')
        category = component.get('category', '')
        
        # Look for carousel.standard components
        return (component_id == 'carousel.standard' and 
                category == 'carousel')
    
    def extract_title_from_carousel(self, carousel_item):
        """Extract title from a carousel item"""
        try:
            # Look for text.title in the carousel structure
            text_obj = carousel_item.get('text', {})
            if isinstance(text_obj, dict):
                title = text_obj.get('title', '')
                if title and isinstance(title, str):
                    return title.strip()
                    
            # Alternative path: look for title in other locations
            title = carousel_item.get('title', '')
            if title and isinstance(title, str):
                return title.strip()
                
        except Exception:
            pass
            
        return None
        
    def extract_carousel_titles_regex(self, text):
        """Extract carousel titles using regex as fallback"""
        carousels = []
        try:
            # Pattern to match carousel.standard components with titles
            # This regex looks for the specific structure you mentioned
            pattern = r'"component":\s*{\s*"id":\s*"carousel\.standard"[^}]*}[^}]*"text":\s*{\s*"title":\s*"([^"]+)"'
            matches = re.findall(pattern, text, re.DOTALL)
            
            for match in matches:
                title = match.strip()
                if title and title not in carousels:
                    carousels.append(title)
                    
            # If no matches with the specific pattern, try a simpler approach
            # but still filter for carousel context
            if not carousels:
                # Look for titles that appear near carousel.standard
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'carousel.standard' in line:
                        # Look in nearby lines for title
                        start = max(0, i - 5)
                        end = min(len(lines), i + 10)
                        context = '\n'.join(lines[start:end])
                        
                        title_pattern = r'"title":\s*"([^"]+)"'
                        title_matches = re.findall(title_pattern, context)
                        for title in title_matches:
                            clean_title = title.strip()
                            if clean_title and clean_title not in carousels:
                                # Filter out logging-like content
                                if not self.is_logging_content(clean_title):
                                    carousels.append(clean_title)
                                    
        except Exception as e:
            carousels = [f"Regex extraction error: {str(e)}"]
            
        return carousels
        
    def is_logging_content(self, text):
        """Check if text appears to be logging content rather than a carousel title"""
        if not text:
            return True
            
        # Filter out common logging patterns
        logging_indicators = [
            'log', 'debug', 'error', 'warn', 'info',
            'timestamp', 'level', 'trace', 'stack',
            'exception', 'request_id', 'correlation_id',
            'session_id', 'user_id', 'api_key'
        ]
        
        text_lower = text.lower()
        for indicator in logging_indicators:
            if indicator in text_lower:
                return True
                
        # Filter out texts that look like IDs or technical strings
        if len(text) > 100:  # Very long titles are likely not carousel titles
            return True
            
        if text.count('_') > 3:  # Too many underscores suggest technical strings
            return True
            
        if text.count('-') > 5:  # Too many dashes suggest IDs
            return True
            
        return False
        
    def display_carousels(self, carousels):
        """Display carousel titles in the carousel tab"""
        content = f"🎠 CAROUSEL TITLES FROM carousel.standard COMPONENTS\n{'='*60}\n\n"
        content += "Extracting titles specifically from:\n"
        content += "• component.id = 'carousel.standard'\n"
        content += "• component.category = 'carousel'\n"
        content += "• text.title field\n\n"
        content += f"{'='*60}\n\n"
        
        if carousels:
            content += f"✅ Found {len(carousels)} carousel title(s):\n\n"
            for i, carousel in enumerate(carousels, 1):
                content += f"  {i:2d}. {carousel}\n"
            content += f"\n📊 Total carousel titles extracted: {len(carousels)}\n"
        else:
            content += "❌ No carousel.standard titles found in response\n"
            content += "\nPossible reasons:\n"
            content += "• No carousel.standard components in response\n"
            content += "• Carousel components don't have text.title fields\n"
            content += "• Response structure may be different than expected\n"
            
        content += f"\n{'='*60}\n"
        self.carousel_text.insert(tk.END, content)
        
    def handle_error(self, error_message):
        """Handle and display errors"""
        self.update_status(f"Error: {error_message}")
        messagebox.showerror("Request Error", error_message)
        self.is_loading = False
        self.request_button.config(state='normal')
        self.progress.stop()
        
    def clear_response(self):
        """Clear all response displays"""
        self.summary_text.delete(1.0, tk.END)
        self.raw_text.delete(1.0, tk.END)
        self.carousel_text.delete(1.0, tk.END)
        
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