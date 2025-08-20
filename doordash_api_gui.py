#!/usr/bin/env python3
"""
DoorDash API GUI Application
A modern GUI for testing DoorDash realtime recommendation API
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import font as tkfont
import requests
import json
import threading
import os
import webbrowser
from datetime import datetime
import re
import subprocess
import shutil
import time

class DoorDashAPIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DoorDash API Tester & Configuration Manager")
        # Start fullscreen to ensure controls are visible without dragging splitters
        try:
            self.root.attributes('-zoomed', True)  # macOS/Linux Tk (zoom to full screen)
        except Exception:
            try:
                self.root.state('zoomed')  # Windows
            except Exception:
                self.root.geometry("1800x1200")
        self.root.configure(bg='#f0f0f0')
        
        # Track DPI/sizing to scale widgets
        self.ui_scale = self.compute_ui_scale()
        self.apply_global_styles()
        
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
            
    def compute_ui_scale(self) -> float:
        try:
            screen_w = self.root.winfo_screenwidth()
            # Base width ~ 1440; scale proportionally
            return max(1.0, min(1.5, screen_w / 1440.0))
        except Exception:
            return 1.0
    
    def choose_font_family(self) -> str:
        try:
            available = {f.lower() for f in tkfont.families()}
            for fam in ["Lato", "Helvetica Neue", "Segoe UI", "Helvetica", "Arial"]:
                if fam.lower() in available:
                    return fam
        except Exception:
            pass
        return "Arial"

    def apply_global_styles(self):
        try:
            style = ttk.Style()
            base_pad = int(8 * self.ui_scale)
            # Choose app font similar to Google's Lato with robust fallbacks
            family = self.choose_font_family()
            base_size = max(10, int(10 * self.ui_scale))
            self.app_font = tkfont.Font(family=family, size=max(9, int(9 * self.ui_scale)))
            self.app_font_bold = tkfont.Font(family=family, size=max(11, int(11*self.ui_scale)), weight='bold')
            # Set defaults for ttk widgets
            style.configure('.', font=self.app_font)
            style.configure('TLabel', font=self.app_font)
            style.configure('TButton', font=self.app_font, padding=(base_pad, max(6, int(6*self.ui_scale))))
            style.configure('Accent.TButton', font=self.app_font, padding=(base_pad+2, max(6, int(7*self.ui_scale))))
            style.configure('TEntry', padding=(max(4, int(4*self.ui_scale)), max(3, int(3*self.ui_scale))))
            style.configure('TNotebook.Tab', font=self.app_font)
            # Also set Tk option database for classic widgets
            try:
                self.root.option_add("*Font", self.app_font)
            except Exception:
                pass
        except Exception:
            pass
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Warning/Error banner at the top
        self.create_warning_banner(main_frame)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 DoorDash API Tester & Configuration Manager", 
                               font=(self.choose_font_family(), 13, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create a PanedWindow to split configuration and response areas
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        try:
            # Start with the sash lower to ensure controls are visible
            self.root.update_idletasks()
            paned_window.sashpos(0, int(self.root.winfo_height()*0.90))
        except Exception:
            pass
        
        # Top pane split horizontally: left (config), right (actions/auth)
        top_pane = ttk.Frame(paned_window)
        paned_window.add(top_pane, weight=3)
        
        hsplit = ttk.PanedWindow(top_pane, orient=tk.HORIZONTAL)
        hsplit.pack(fill=tk.BOTH, expand=True)
        
        left_config = ttk.Frame(hsplit)
        right_actions = ttk.Frame(hsplit, width=420)
        hsplit.add(left_config, weight=3)
        hsplit.add(right_actions, weight=1)
        try:
            # ensure right panel reasonable width
            hsplit.sashpos(0, int(self.root.winfo_width()*0.62))
        except Exception:
            pass
        
        # Left: Configuration notebook
        self.create_config_section(left_config)
        
        # Right: Actions + Auth sidebar (buttons always visible)
        self.create_actions_sidebar(right_actions)
        
        # Bottom pane for response area
        response_frame = ttk.Frame(paned_window)
        paned_window.add(response_frame, weight=2)  # Response area gets less weight
        
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
        
        # Experiments tab
        self.experiments_tab = ttk.Frame(self.response_notebook)
        self.response_notebook.add(self.experiments_tab, text="🧪 Experiments")
        
        self.experiments_display = scrolledtext.ScrolledText(self.experiments_tab, wrap=tk.WORD, 
                                                           font=('Consolas', 10))
        self.experiments_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Output tab for YAML generation
        self.output_tab = ttk.Frame(self.response_notebook)
        self.response_notebook.add(self.output_tab, text="📄 Output")
        
        # Create a container for the output tab content
        output_container = ttk.Frame(self.output_tab)
        output_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and instructions
        output_title = ttk.Label(output_container, text="📄 Experiment YAML Output", 
                                font=('Arial', 14, 'bold'))
        output_title.pack(pady=(0, 10))
        
        # Instructions
        instructions_text = "Generated YAML configurations will appear here. Use the YAML Generator tab to create experiment configs."
        ttk.Label(output_container, text=instructions_text, font=('Arial', 10), 
                 foreground='gray').pack(pady=(0, 15))
        
        # YAML output text area
        self.yaml_output_display = scrolledtext.ScrolledText(output_container, wrap=tk.WORD, 
                                                           font=('Consolas', 10))
        self.yaml_output_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Control buttons
        output_buttons_frame = ttk.Frame(output_container)
        output_buttons_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(output_buttons_frame, text="📋 Copy to Clipboard", 
                  command=self.copy_yaml_output).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(output_buttons_frame, text="🧹 Clear Output", 
                  command=self.clear_yaml_output).pack(side=tk.LEFT)
        ttk.Button(output_buttons_frame, text="🔄 Switch to YAML Generator", 
                  command=self.switch_to_yaml_generator).pack(side=tk.RIGHT)
        
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
        # Add title label instead of LabelFrame border
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(title_frame, text="📋 Configuration Editor", 
                 font=(self.choose_font_family(), 11, 'bold')).pack(anchor=tk.W)
        
        config_frame = ttk.Frame(parent, padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create notebook for organized config sections
        self.config_notebook = ttk.Notebook(config_frame)
        self.config_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Set minimum height for the notebook
        config_frame.configure(height=400)
        
        # Initialize config variables dictionary
        self.config_vars = {}
        
        # Create different tabs for organized configuration
        self.create_api_config_tab()
        self.create_headers_config_tab()
        self.create_location_config_tab()
        self.create_misc_config_tab()
        self.create_experiment_config_tab()
        self.create_charles_proxy_tab()
        self.create_yaml_generator_tab()
        
        # Config buttons were moved to right sidebar actions to be always visible
                
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
        
        # Export as curl button
        ttk.Button(controls_frame, text="📋 Export as cURL", 
                  command=self.export_as_curl).pack(side=tk.LEFT, padx=(0, 10))
        
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
            # Show enhanced JWT error dialog
            self.show_jwt_error_dialog("JWT Token Required", 
                                     "A JWT authorization token is required to make API requests.")
            # Re-check after dialog
            token = self.config.get('AUTHORIZATION_TOKEN', '')
            if not token or token.lower() == 'null' or not token.strip():
                raise Exception("Authorization token is required but not set")
                
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
        
        # Scrollable frame with improved layout
        canvas = tk.Canvas(api_frame)
        scrollbar = ttk.Scrollbar(api_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure canvas to expand scrollable_frame to full width
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make scrollable_frame fill the canvas width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Ensure canvas is properly initialized
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', configure_scroll_region)
        scrollable_frame.bind('<Configure>', configure_scroll_region)
        
        # API configuration fields - now with better spacing and layout
        content_frame = ttk.Frame(scrollable_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        ttk.Label(content_frame, text="🔌 API Connection", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 15), anchor='w')
        
        # Base URL field
        self.create_api_host_field_with_presets(content_frame)
        
        self.create_config_field(content_frame, "Experience ID", "EXPERIENCE_ID", 
                               "Application experience identifier")
        
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        ttk.Label(content_frame, text="🔑 Authentication", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 15), anchor='w')
        
        self.create_config_field(content_frame, "Authorization Token", "AUTHORIZATION_TOKEN", 
                               "JWT Bearer token", is_password=False)
        
        # Fetch from Android Logs button
        auth_buttons = ttk.Frame(content_frame)
        auth_buttons.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(auth_buttons, text="🔍 Fetch from Android Logs", command=self.open_fetch_auth_from_android_modal).pack(side=tk.LEFT)
        
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        ttk.Label(content_frame, text="📱 Client Information", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 15), anchor='w')
        
        self.create_config_field(content_frame, "User Agent", "USER_AGENT", 
                               "Client user agent string")
        self.create_config_field(content_frame, "Client Version", "CLIENT_VERSION", 
                               "Application version")
        
        # Client preset buttons
        client_preset_frame = ttk.Frame(content_frame)
        client_preset_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(client_preset_frame, text="📱 iOS Prod", 
                  command=self.apply_ios_prod_preset, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(client_preset_frame, text="🤖 Android Prod", 
                  command=self.apply_android_prod_preset, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(client_preset_frame, text="🛠️ Android Debug", 
                  command=self.apply_android_debug_preset, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(client_preset_frame, text="🌐 Web Chrome", 
                  command=self.apply_web_chrome_preset, 
                  width=15).pack(side=tk.LEFT)
        
        # Add some bottom padding
        ttk.Frame(content_frame, height=30).pack()
        
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
        
        # Location preset buttons
        location_preset_frame = ttk.Frame(scrollable_frame)
        location_preset_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(location_preset_frame, text="🏢 SF Office", 
                  command=self.apply_sf_office_preset, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(location_preset_frame, text="🗽 NY Office", 
                  command=self.apply_ny_office_preset, 
                  width=15).pack(side=tk.LEFT)
        
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
        ttk.Label(scrollable_frame, text="🎯 Events & Data", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 10))
        
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
        
        ttk.Label(scrollable_frame, text="🔧 API Configuration", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "BFF Error Format", "BFF_ERROR_FORMAT", 
                               "Backend error format version")
        self.create_config_field(scrollable_frame, "Support Partner Dashpass", "SUPPORT_PARTNER_DASHPASS", 
                               "Enable partner dashpass support")
        self.create_config_field(scrollable_frame, "Cursor", "CURSOR", 
                               "Pagination cursor (set to null to exclude)", width=60)
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(scrollable_frame, text="📊 Display Settings", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 10))
        
        self.create_config_field(scrollable_frame, "Default Verbose", "DEFAULT_VERBOSE", 
                               "Default verbose mode (true/false)")
        self.create_config_field(scrollable_frame, "Max Verbose Lines", "MAX_VERBOSE_LINES", 
                               "Maximum lines in verbose output")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_charles_proxy_tab(self):
        """Create Charles Proxy configuration tab"""
        proxy_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(proxy_frame, text="🌐 Charles Proxy")
        
        # Main container with padding
        main_container = ttk.Frame(proxy_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Title
        title_label = ttk.Label(main_container, text="🌐 Charles Proxy Configuration", 
                               font=(self.choose_font_family(), 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """Configure Charles Proxy settings for intercepting and analyzing network traffic.
This is useful for debugging API calls and inspecting request/response data."""
        ttk.Label(main_container, text=desc_text, font=('Arial', 10), 
                 foreground='gray', wraplength=600).pack(pady=(0, 20))
        
        # Proxy configuration section
        config_frame = ttk.LabelFrame(main_container, text="Proxy Settings", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Proxy URL field
        url_frame = ttk.Frame(config_frame)
        url_frame.pack(fill=tk.X, pady=5)
        ttk.Label(url_frame, text="Proxy URL:", font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT)
        
        proxy_url_var = tk.StringVar(value=self.config.get('CHARLES_PROXY_URL', '127.0.0.1'))
        self.config_vars['CHARLES_PROXY_URL'] = proxy_url_var
        
        proxy_url_entry = ttk.Entry(url_frame, textvariable=proxy_url_var, width=30)
        proxy_url_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Proxy Port field
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=5)
        ttk.Label(port_frame, text="Proxy Port:", font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT)
        
        proxy_port_var = tk.StringVar(value=self.config.get('CHARLES_PROXY_PORT', '8888'))
        self.config_vars['CHARLES_PROXY_PORT'] = proxy_port_var
        
        proxy_port_entry = ttk.Entry(port_frame, textvariable=proxy_port_var, width=10)
        proxy_port_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Android Emulator section
        emulator_frame = ttk.LabelFrame(main_container, text="Android Emulator Setup", padding=15)
        emulator_frame.pack(fill=tk.X, pady=(0, 20))
        
        emulator_desc = """Set up an Android emulator with Charles Proxy for network traffic analysis.
The emulator will be configured to route traffic through the specified proxy."""
        ttk.Label(emulator_frame, text=emulator_desc, font=('Arial', 10), 
                 foreground='gray', wraplength=600).pack(pady=(0, 15))
        
        # AVD Selection
        avd_frame = ttk.Frame(emulator_frame)
        avd_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(avd_frame, text="AVD Name:", font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT)
        
        avd_name_var = tk.StringVar(value=self.config.get('ANDROID_AVD_NAME', 'Pixel_9_Pro_-_Charles'))
        self.config_vars['ANDROID_AVD_NAME'] = avd_name_var
        
        avd_entry = ttk.Entry(avd_frame, textvariable=avd_name_var, width=30)
        avd_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(avd_frame, text="🔍 Auto-detect", 
                  command=self.auto_detect_avd).pack(side=tk.LEFT, padx=(10, 0))
        
        # Emulator controls
        controls_frame = ttk.Frame(emulator_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controls_frame, text="🚀 Start Emulator", 
                  command=self.setup_android_emulator).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="📱 List Available Emulators", 
                  command=self.list_android_emulators).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="🔧 Configure Proxy on Device", 
                  command=self.configure_proxy_on_device).pack(side=tk.LEFT)
        
        # Status display
        status_frame = ttk.Frame(emulator_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.proxy_status_var = tk.StringVar(value="Ready to configure emulator")
        ttk.Label(status_frame, textvariable=self.proxy_status_var, 
                 font=('Arial', 9), foreground='blue').pack(anchor=tk.W)
        
        # Instructions section
        instructions_frame = ttk.LabelFrame(main_container, text="Setup Instructions", padding=15)
        instructions_frame.pack(fill=tk.X)
        
        instructions_text = """1. Ensure Charles Proxy is running on your machine
2. Note the proxy URL and port from Charles Proxy settings
3. Click "Create & Start Emulator" to set up a new Android emulator
4. The emulator will be configured to route traffic through Charles Proxy
5. Install and run your Android app on the emulator
6. All network traffic will be visible in Charles Proxy

Note: This requires Android SDK and AVD Manager to be properly configured."""
        
        ttk.Label(instructions_frame, text=instructions_text, font=('Arial', 9), 
                 justify=tk.LEFT, wraplength=600).pack(anchor='w')

    def create_experiment_config_tab(self):
        """Create a simple placeholder experiment config tab"""
        exp_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(exp_frame, text="🧪 Experiments")
        
        # Simple placeholder content
        placeholder_frame = ttk.Frame(exp_frame)
        placeholder_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(placeholder_frame, text="🧪 Experiment Configuration", 
                               font=(self.choose_font_family(), 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        info_text = """The experiment YAML generator has been moved to its own dedicated tab:

📄 Look for the "YAML Generator" tab at the top of this window.

This provides a better experience for creating experiment configurations with:
• Step-by-step Unity content parsing
• Manual field entry
• Automatic YAML generation
• Email validation
• Copy to clipboard functionality"""
        
        ttk.Label(placeholder_frame, text=info_text, font=('Arial', 11), 
                 justify=tk.LEFT).pack(anchor='w')

    def create_yaml_generator_tab(self):
        """Create the main YAML generator tab"""
        yaml_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(yaml_frame, text="📄 YAML Generator")
        
        # Main container with padding
        main_container = ttk.Frame(yaml_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Title
        title_label = ttk.Label(main_container, text="📄 Experiment YAML Configuration Generator", 
                               font=(self.choose_font_family(), 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Button to open Unity content parser modal
        parse_button_frame = ttk.Frame(main_container)
        parse_button_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(parse_button_frame, text="📄 Parse Unity Content", 
                  command=self.open_unity_parser_modal,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(parse_button_frame, text="Paste Unity experiment page content to auto-fill fields", 
                 font=('Arial', 10), foreground='gray').pack(side=tk.LEFT, padx=(10, 0))
        
        # Manual entry form (no tabs needed now)
        form_frame = ttk.LabelFrame(main_container, text="📝 Experiment Configuration", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Initialize experiment variables
        self.exp_vars = {}
        
        self.create_manual_experiment_form(form_frame)
        
        # Action buttons
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(action_frame, text="🔄 Generate YAML", 
                  command=self.generate_experiment_yaml,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="📄 View Output Tab", 
                  command=self.switch_to_output_tab).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="🧹 Clear All Fields", 
                  command=self.clear_all_experiment_fields).pack(side=tk.LEFT)

    def create_manual_experiment_form(self, parent):
        """Create manual experiment entry form"""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        content_frame = ttk.Frame(scrollable_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Experiment configuration fields
        ttk.Label(content_frame, text="🔧 Basic Configuration", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 15), anchor='w')
        
        self.exp_vars['key'] = self.create_experiment_field(content_frame, "Experiment Key", "key", 
                                                           "e.g., cx_homepage_discovery_realtime_android_v3", width=60)
        self.exp_vars['description'] = self.create_experiment_field(content_frame, "Description", "description", 
                                                                   "Brief description of the experiment", width=60)
        
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        ttk.Label(content_frame, text="⚙️ Experiment Settings", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 15), anchor='w')
        
        self.exp_vars['returnType'] = self.create_experiment_field(content_frame, "Return Type", "returnType", 
                                                                   "Boolean or String", width=20)
        self.exp_vars['defaultValue'] = self.create_experiment_field(content_frame, "Default Value", "defaultValue", 
                                                                    "false (Boolean) or control (String)", width=20)
        self.exp_vars['expiration'] = self.create_experiment_field(content_frame, "Expiration Date", "expiration", 
                                                                  "Format: YYYY-MM-DD", width=30)
        
        # Add smart default value logic based on return type
        def update_default_value(*args):
            return_type = self.exp_vars['returnType'].get().strip().lower()
            current_default = self.exp_vars['defaultValue'].get().strip()
            
            # Only auto-update if the field is empty or has a standard default
            if not current_default or current_default.lower() in ['false', 'control', 'true']:
                if 'string' in return_type:
                    self.exp_vars['defaultValue'].set('control')
                elif 'boolean' in return_type:
                    self.exp_vars['defaultValue'].set('false')
        
        # Use trace_add for newer Tkinter versions, fallback to trace for older ones
        try:
            self.exp_vars['returnType'].trace_add('write', update_default_value)
        except AttributeError:
            self.exp_vars['returnType'].trace('w', update_default_value)
        
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        ttk.Label(content_frame, text="👤 Ownership & Metadata", font=(self.choose_font_family(), 11, 'bold')).pack(pady=(0, 15), anchor='w')
        
        self.exp_vars['owner'] = self.create_experiment_field(content_frame, "Owner Email", "owner", 
                                                             "Owner's email address", width=50)
        
        # Add real-time email validation for owner field
        def validate_owner_email(*args):
            email = self.exp_vars['owner'].get()
            if email:
                formatted_email = self.format_email(email)
                if formatted_email != email:
                    # Auto-format the email
                    self.exp_vars['owner'].set(formatted_email)
        
        # Use trace_add for newer Tkinter versions, fallback to trace for older ones
        try:
            self.exp_vars['owner'].trace_add('write', validate_owner_email)
        except AttributeError:
            self.exp_vars['owner'].trace('w', validate_owner_email)
        self.exp_vars['url'] = self.create_experiment_field(content_frame, "Unity URL", "url", 
                                                           "Full Unity experiment URL", width=80)
        self.exp_vars['type'] = self.create_experiment_field(content_frame, "Type", "type", 
                                                            "Usually 'Experiment'", width=30)
        self.exp_vars['group'] = self.create_experiment_field(content_frame, "Group", "group", 
                                                             "e.g., DiscoveryExperience", width=40)
        
        # Set default values
        self.exp_vars['returnType'].set('Boolean')
        self.exp_vars['defaultValue'].set('false')
        self.exp_vars['type'].set('Experiment')
        self.exp_vars['group'].set('DiscoveryExperience')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")



    def create_experiment_field(self, parent, label, key, description="", width=50):
        """Create an experiment configuration field"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)
        
        # Label
        label_widget = ttk.Label(frame, text=f"{label}:", font=('Arial', 9, 'bold'), width=20)
        label_widget.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry variable
        var = tk.StringVar()
        
        # Entry widget
        entry = ttk.Entry(frame, textvariable=var, width=width)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Description label if provided
        if description:
            desc_label = ttk.Label(frame, text=description, font=('Arial', 8), 
                                 foreground='gray')
            desc_label.pack(side=tk.RIGHT)
            
        return var



    def extract_fields_from_text(self, content):
        """Extract experiment fields from Unity page text content"""
        extracted_data = {}
        lines = content.split('\n')
        
        # Clean and normalize lines
        clean_lines = [line.strip() for line in lines if line.strip()]
        
        # Extract experiment key (usually first line or after certain patterns)
        for i, line in enumerate(clean_lines):
            # Look for experiment key patterns - longer snake_case names
            if re.match(r'^[a-z][a-z0-9_]*[a-z0-9]$', line) and len(line) > 5:
                # Skip common non-experiment words
                if line not in ['type', 'experiment', 'return', 'owner', 'vertical', 'consumer', 'last', 'updated', 'start', 'date', 'end', 'configure', 'test', 'monitor', 'debug', 'implement', 'history', 'details']:
                    extracted_data['key'] = line
                    break
        
        # Extract fields using keyword matching
        for i, line in enumerate(clean_lines):
            line_lower = line.lower()
            
            # Extract owner
            if 'owner' in line_lower and i + 1 < len(clean_lines):
                next_line = clean_lines[i + 1]
                # Look for names or email addresses
                if '@' in next_line or any(name_part in next_line.lower() for name_part in ['harsh', 'alkutkar']):
                    formatted_email = self.format_email(next_line)
                    extracted_data['owner'] = formatted_email
            
            # Extract type
            if 'type' in line_lower and i + 1 < len(clean_lines):
                next_line = clean_lines[i + 1]
                if next_line.lower() in ['experiment', 'feature', 'config']:
                    extracted_data['type'] = next_line
            
            # Extract return type for default value
            if 'return type' in line_lower and i + 1 < len(clean_lines):
                next_line = clean_lines[i + 1].lower()
                if 'boolean' in next_line:
                    extracted_data['defaultValue'] = 'false'  # Default for boolean experiments
                elif 'string' in next_line:
                    extracted_data['defaultValue'] = 'control'  # Default for string experiments
                # Store the return type for later reference
                extracted_data['returnType'] = next_line.title()  # Store as Boolean/String
            
            # Extract description from Problem Statement
            if 'problem statement' in line_lower and i + 1 < len(clean_lines):
                next_line = clean_lines[i + 1]
                if len(next_line) > 20:  # Reasonable description length
                    extracted_data['description'] = next_line
            
            # Extract dates
            if any(date_keyword in line_lower for date_keyword in ['start date', 'end date', 'date']):
                # Look for date patterns in current and next lines
                for check_line in [line, clean_lines[i + 1] if i + 1 < len(clean_lines) else '']:
                    # Find all dates in the line (YYYY-MM-DD format)
                    date_matches = re.findall(r'(\d{4}-\d{2}-\d{2})', check_line)
                    if date_matches:
                        # If multiple dates found (start - end format), take the last one (end date)
                        if len(date_matches) > 1:
                            extracted_data['expiration'] = date_matches[-1]  # Last date is end date
                        else:
                            # Single date - check if it's an end date context
                            if 'end' in line_lower or any(year in check_line for year in ['2026', '2027', '2028']):
                                extracted_data['expiration'] = date_matches[0]
                        break
        
        return extracted_data

    def clear_content_text(self):
        """Clear the content text area"""
        self.content_text.delete(1.0, tk.END)

    def open_fetch_auth_from_android_modal(self):
        """Open modal to guide and fetch JWT from Android adb logs"""
        modal = tk.Toplevel(self.root)
        modal.title("Fetch Authorization from Android Logs")
        modal.geometry("780x420")
        modal.resizable(True, True)
        modal.transient(self.root)
        modal.grab_set()
        
        container = ttk.Frame(modal, padding=15)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="🔑 Fetch Authorization Token from Android Debug Logs", font=(self.choose_font_family(), 11, 'bold')).pack(anchor='w', pady=(0, 10))
        
        steps = (
            "1) Ensure a device/emulator is connected: adb devices\n"
            "2) Run the DEBUG build of the Android app and login\n"
            "3) We will scan logcat for lines containing 'Authorization: JWT ...'\n"
            "4) The token will be extracted and pre-filled here"
        )
        ttk.Label(container, text=steps, font=('Consolas', 10), foreground='gray').pack(anchor='w')
        
        # Status area
        status_frame = ttk.LabelFrame(container, text="Status", padding=8)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        self.adb_status = scrolledtext.ScrolledText(status_frame, height=8, wrap=tk.WORD, font=('Consolas', 10))
        self.adb_status.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btns = ttk.Frame(container)
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="🌐 ADB Setup Guide", command=self.open_adb_setup_url).pack(side=tk.LEFT)
        ttk.Button(btns, text="🔎 Scan Logs", command=self.scan_adb_for_jwt_threaded).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btns, text="Close", command=modal.destroy).pack(side=tk.RIGHT)
        
        # Initial check
        self.append_adb_status("Ready. Click 'Scan Logs' after logging in on the Android debug app.\n")
        
    def open_adb_setup_url(self):
        webbrowser.open("https://developer.android.com/tools/adb")
    
    def append_adb_status(self, text: str):
        try:
            self.adb_status.insert(tk.END, text)
            self.adb_status.see(tk.END)
        except Exception:
            pass
    
    def scan_adb_for_jwt_threaded(self):
        thread = threading.Thread(target=self.scan_adb_for_jwt)
        thread.daemon = True
        thread.start()
    
    def scan_adb_for_jwt(self):
        # Verify adb exists - check common locations on macOS
        adb_path = shutil.which('adb')
        if not adb_path:
            # Check common homebrew locations
            common_paths = [
                '/opt/homebrew/bin/adb',  # Apple Silicon Homebrew
                '/usr/local/bin/adb',     # Intel Homebrew
                '/usr/local/android-sdk/platform-tools/adb',
                '~/Library/Android/sdk/platform-tools/adb',
                '~/Android/Sdk/platform-tools/adb'
            ]
            
            for path in common_paths:
                expanded_path = os.path.expanduser(path)
                if os.path.isfile(expanded_path) and os.access(expanded_path, os.X_OK):
                    adb_path = expanded_path
                    break
            
            if not adb_path:
                self.append_adb_status("❌ adb not found in PATH or common locations.\n")
                self.append_adb_status("💡 Install Android Platform-Tools:\n")
                self.append_adb_status("   • Via Homebrew: brew install android-platform-tools\n")
                self.append_adb_status("   • Or download from: https://developer.android.com/studio/releases/platform-tools\n")
                return
        
        self.append_adb_status(f"✅ Found adb at {adb_path}\n")
        self.append_adb_status("🔎 Scanning logs for Authorization header...\n")
        
        # Run logcat -d to dump recent logs quickly
        try:
            result = subprocess.run([adb_path, 'logcat', '-d'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        except Exception as e:
            self.append_adb_status(f"❌ Failed to run adb logcat: {e}\n")
            return
        
        if result.returncode != 0:
            self.append_adb_status(f"❌ adb logcat error: {result.stderr}\n")
            return
        
        logs = result.stdout
        # Look for Authorization: JWT <token>
        match = re.search(r"Authorization:\s*JWT\s+([A-Za-z0-9-_\.]+)", logs)
        if not match:
            self.append_adb_status("⚠️ Could not find Authorization: JWT ... in logs. Make sure you're on DEBUG build and logged in.\n")
            return
        
        jwt = match.group(1)
        # Set both GUI field and in-memory config so requests use it immediately
        self.config['AUTHORIZATION_TOKEN'] = jwt
        if 'AUTHORIZATION_TOKEN' in self.config_vars:
            self.config_vars['AUTHORIZATION_TOKEN'].set(jwt)
        
        self.append_adb_status("✅ Token found and pre-filled in Authorization Token field.\n")
        
    def validate_email(self, email):
        """Validate email format and ensure it's a @doordash.com email"""
        if not email:
            return False, "Email is required"
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Check for @doordash.com domain
        if not email.lower().endswith('@doordash.com'):
            return False, "Email must be a @doordash.com address"
        
        # Additional checks for proper DoorDash email format
        local_part = email.split('@')[0]
        
        # Check if local part is reasonable (only letters, numbers, dots, and underscores)
        if not re.match(r'^[a-zA-Z0-9._]+$', local_part):
            return False, "Email contains invalid characters before @doordash.com"
        
        # Check for reasonable length
        if len(local_part) < 2:
            return False, "Email username is too short"
        
        if len(local_part) > 50:
            return False, "Email username is too long"
        
        return True, "Valid email"

    def format_email(self, input_text):
        """Format and clean email input"""
        if not input_text:
            return ""
        
        # Clean the input
        email = input_text.strip().lower()
        
        # If it looks like a name without @doordash.com, try to construct the email
        if '@' not in email:
            # Convert spaces to dots and remove special characters
            cleaned_name = re.sub(r'[^a-zA-Z0-9\s.-]', '', email)
            cleaned_name = re.sub(r'\s+', '.', cleaned_name.strip())
            email = f"{cleaned_name}@doordash.com"
        
        # Fix common domain typos
        email = re.sub(r'@doordash\.co$', '@doordash.com', email)
        email = re.sub(r'@dd\.com$', '@doordash.com', email)
        
        return email

    def generate_experiment_yaml(self):
        """Generate YAML configuration from current form values"""
        # Get all values from form
        values = {}
        for key, var in self.exp_vars.items():
            values[key] = var.get().strip()
        
        # Validate required fields
        required_fields = ['key', 'description', 'defaultValue', 'expiration', 'owner', 'url', 'type', 'group']
        missing_fields = [field for field in required_fields if not values.get(field)]
        
        if missing_fields:
            messagebox.showwarning("Missing Fields", 
                                 f"Please fill in the following required fields:\n\n" + 
                                 "\n".join([f"• {field}" for field in missing_fields]))
            return
        
        # Validate email format
        email_valid, email_message = self.validate_email(values['owner'])
        if not email_valid:
            messagebox.showerror("Invalid Email", 
                               f"Owner email validation failed:\n\n{email_message}\n\n"
                               f"Please use a valid @doordash.com email address.\n"
                               f"Example: harsh.alkutkar@doordash.com")
            return
        
        # Validate Unity URL format (warning only, don't stop generation)
        self.validate_unity_url(values['url'])
        
        # Use the internal method to generate YAML
        self.generate_experiment_yaml_internal(values)
        
        messagebox.showinfo("YAML Generated", "Experiment YAML configuration has been generated successfully!\n\nCheck the 'Output' tab to view the result.")



    def clear_all_experiment_fields(self):
        """Clear all experiment configuration fields"""
        for var in self.exp_vars.values():
            var.set("")
        messagebox.showinfo("Fields Cleared", "All experiment configuration fields have been cleared.")

    def open_unity_parser_modal(self):
        """Open modal dialog for Unity content parsing"""
        # Create modal window
        modal = tk.Toplevel(self.root)
        modal.title("Parse Unity Content")
        modal.geometry("900x520")
        modal.resizable(True, True)
        
        # Make it modal
        modal.transient(self.root)
        modal.grab_set()
        
        # Center the modal
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (900 // 2)
        y = (modal.winfo_screenheight() // 2) - (520 // 2)
        modal.geometry(f"900x520+{x}+{y}")
        
        # Main container
        main_frame = ttk.Frame(modal)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="📄 Parse Unity Experiment Content", 
                               font=(self.choose_font_family(), 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="📋 Instructions", padding=10)
        instructions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Unity link button
        link_frame = ttk.Frame(instructions_frame)
        link_frame.pack(fill=tk.X, pady=(0, 10))
        
        def open_unity_experiments():
            import webbrowser
            webbrowser.open("https://unity.doordash.com/suites/data/decision-systems/dynamic-values-v2/experiments")
        
        ttk.Button(link_frame, text="🌐 Open Unity Experiments", 
                  command=open_unity_experiments).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(link_frame, text="→ Navigate to your experiment page", 
                 font=('Arial', 10), foreground='gray').pack(side=tk.LEFT)
        
        # Instructions text
        instructions_text = """1. Click "🌐 Open Unity Experiments" above or navigate to your experiment page
2. Press Cmd+A (Mac) or Ctrl+A (Windows) to select all content
3. Press Cmd+C (Mac) or Ctrl+C (Windows) to copy
4. Paste the content in the text area below
5. Click "Parse Content" to extract experiment fields"""
        
        ttk.Label(instructions_frame, text=instructions_text, font=('Arial', 10)).pack(anchor='w')
        
        # Example section (compact)
        example_frame = ttk.LabelFrame(main_frame, text="📖 Example Content", padding=10)
        example_frame.pack(fill=tk.X, pady=(0, 15))
        
        example_text = """enable_mx_preview_v2
Type: Experiment
Return Type: String
Owner: Harsh Alkutkar
Start Date - End Date: 2025-02-11 - 2025-06-30"""
        
        ttk.Label(example_frame, text=example_text, font=('Consolas', 9), 
                 foreground='gray').pack(anchor='w')
        
        # Content input area (fixed height)
        content_frame = ttk.LabelFrame(main_frame, text="Unity Page Content", padding=10)
        content_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Text area with scrollbar (3 lines height)
        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                               font=('Consolas', 10), height=3)
        content_text.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons (always visible at bottom)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0), side=tk.BOTTOM)
        
        def parse_and_close():
            content = content_text.get(1.0, tk.END).strip()
            if content:
                # Parse the content
                extracted_data = self.extract_fields_from_text(content)
                
                # Update fields with extracted data
                fields_updated = []
                
                if extracted_data.get('key'):
                    self.exp_vars['key'].set(extracted_data['key'])
                    fields_updated.append("Key")
                    
                if extracted_data.get('owner'):
                    self.exp_vars['owner'].set(extracted_data['owner'])
                    fields_updated.append("Owner")
                    
                if extracted_data.get('expiration'):
                    self.exp_vars['expiration'].set(extracted_data['expiration'])
                    fields_updated.append("Expiration")
                    
                if extracted_data.get('defaultValue'):
                    self.exp_vars['defaultValue'].set(extracted_data['defaultValue'])
                    fields_updated.append("Default Value")
                    
                if extracted_data.get('returnType'):
                    self.exp_vars['returnType'].set(extracted_data['returnType'])
                    fields_updated.append("Return Type")
                    
                if extracted_data.get('type'):
                    self.exp_vars['type'].set(extracted_data['type'])
                    fields_updated.append("Type")
                
                if extracted_data.get('description'):
                    self.exp_vars['description'].set(extracted_data['description'])
                    fields_updated.append("Description")
                
                # Close modal
                modal.destroy()
                
                # Show results and auto-generate
                if fields_updated:
                    message = f"✅ Successfully parsed the following fields:\n\n• " + "\n• ".join(fields_updated)
                    messagebox.showinfo("Parsing Complete", message)
                    
                    # Auto-generate YAML after a short delay
                    self.root.after(500, self.auto_generate_yaml_after_parsing)
                else:
                    messagebox.showwarning("No Fields Found", 
                                         "Could not extract any experiment fields from the provided content.")
            else:
                messagebox.showwarning("No Content", "Please paste Unity page content to parse")
        
        def clear_content():
            content_text.delete(1.0, tk.END)
        
        ttk.Button(button_frame, text="🔍 Parse Content", 
                  command=parse_and_close).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🧹 Clear", 
                  command=clear_content).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=modal.destroy).pack(side=tk.RIGHT)
        
        # Focus on text area
        content_text.focus_set()

    def copy_yaml_output(self):
        """Copy YAML output from the main Output tab to clipboard"""
        yaml_content = self.yaml_output_display.get(1.0, tk.END).strip()
        if not yaml_content:
            messagebox.showwarning("No Content", "No YAML content to copy")
            return
            
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(yaml_content)
            messagebox.showinfo("Copied", "YAML content copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy to clipboard: {str(e)}")

    def clear_yaml_output(self):
        """Clear the YAML output area"""
        self.yaml_output_display.delete(1.0, tk.END)

    def switch_to_yaml_generator(self):
        """Switch to the YAML Generator tab"""
        # Find the YAML Generator tab index
        for i in range(self.config_notebook.index("end")):
            if "YAML Generator" in self.config_notebook.tab(i, "text"):
                self.config_notebook.select(i)
                break

    def switch_to_output_tab(self):
        """Switch to the Output tab in the response area"""
        # Find the Output tab index
        for i in range(self.response_notebook.index("end")):
            if "Output" in self.response_notebook.tab(i, "text"):
                self.response_notebook.select(i)
                break

    def validate_unity_url(self, url):
        """Validate Unity URL format and show warning banner if invalid"""
        if not url:
            return True  # Empty URL is OK
        
        # Expected Unity URL pattern
        unity_pattern = r'https://unity\.doordash\.com/suites/data/decision-systems/dynamic-values-v2/experiments/[a-f0-9-]+'
        
        if not re.match(unity_pattern, url):
            # Show warning banner
            warning_message = (
                f"⚠️ Unity URL Format Warning: The provided URL doesn't match the expected Unity experiment format.\n"
                f"Expected: https://unity.doordash.com/suites/data/decision-systems/dynamic-values-v2/experiments/[experiment-id]\n"
                f"Provided: {url}\n"
                f"YAML generation will continue, but please verify the URL is correct."
            )
            self.show_warning_banner(warning_message)
            return False
        else:
            # Clear any existing warning if URL is now valid
            self.clear_warning_banner()
            return True

    def show_warning_banner(self, message):
        """Show a warning banner at the top of the application"""
        # Check if warning banner already exists
        if hasattr(self, 'warning_banner') and self.warning_banner.winfo_exists():
            self.warning_banner.destroy()
        
        # Create warning banner
        self.warning_banner = ttk.Frame(self.root, style='Warning.TFrame')
        self.warning_banner.pack(fill=tk.X, padx=5, pady=(5, 0), before=self.root.winfo_children()[0])
        
        # Configure warning style
        style = ttk.Style()
        style.configure('Warning.TFrame', background='#fff3cd', relief='solid', borderwidth=1)
        style.configure('Warning.TLabel', background='#fff3cd', foreground='#856404')
        
        # Warning icon and message
        warning_container = ttk.Frame(self.warning_banner, style='Warning.TFrame')
        warning_container.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Label(warning_container, text="⚠️", font=('Arial', 12), 
                 style='Warning.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(warning_container, text=message, font=('Arial', 9), 
                 style='Warning.TLabel', wraplength=1200).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Close button
        close_btn = ttk.Button(warning_container, text="✕", width=3,
                              command=self.clear_warning_banner)
        close_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def clear_warning_banner(self):
        """Clear the warning banner"""
        if hasattr(self, 'warning_banner') and self.warning_banner.winfo_exists():
            self.warning_banner.destroy()

    def auto_generate_yaml_after_parsing(self):
        """Automatically generate YAML after successful parsing, with validation"""
        try:
            # Get all values from form
            values = {}
            for key, var in self.exp_vars.items():
                values[key] = var.get().strip()
            
            # Check if we have enough fields to attempt auto-generation
            critical_fields = ['key', 'owner', 'type']
            missing_critical = [field for field in critical_fields if not values.get(field)]
            
            if missing_critical:
                # Don't auto-generate if critical fields are missing
                return
            
            # Try to fill in default values for missing fields
            if not values.get('description'):
                values['description'] = f"Experiment configuration for {values['key']}"
            
            if not values.get('defaultValue'):
                # Smart default based on return type if available
                return_type = values.get('returnType', '').lower()
                if 'string' in return_type:
                    values['defaultValue'] = 'control'
                else:
                    values['defaultValue'] = 'false'  # Default for boolean or unknown types
                self.exp_vars['defaultValue'].set(values['defaultValue'])
            
            if not values.get('expiration'):
                # Set a default expiration date (6 months from now)
                from datetime import datetime, timedelta
                future_date = datetime.now() + timedelta(days=180)
                values['expiration'] = future_date.strftime('%Y-%m-%d')
                self.exp_vars['expiration'].set(values['expiration'])
            
            if not values.get('url'):
                values['url'] = 'https://unity.doordash.com/suites/data/decision-systems/dynamic-values-v2/experiments/[experiment-id]'
                self.exp_vars['url'].set(values['url'])
            
            if not values.get('group'):
                values['group'] = 'DiscoveryExperience'
                self.exp_vars['group'].set(values['group'])
            
            # Validate email format
            email_valid, email_message = self.validate_email(values['owner'])
            if not email_valid:
                # Don't auto-generate if email is invalid
                return
            
            # Validate Unity URL format (warning only, continue generation)
            self.validate_unity_url(values['url'])
            
            # All validations passed, generate YAML
            self.generate_experiment_yaml_internal(values)
            
        except Exception as e:
            # If auto-generation fails, silently continue - user can manually generate
            pass

    def generate_experiment_yaml_internal(self, values):
        """Internal method to generate YAML from provided values"""
        # Generate YAML-like output
        # Extract the meaningful part for the top-level entry 
        # Example: "cx_homepage_discovery_realtime_android_v3" -> "discoveryRealtimeV3"
        full_key = values['key']
        
        # Try to extract the meaningful middle part (discovery_realtime_v3) and convert to camelCase
        if 'discovery_realtime' in full_key:
            # For discovery realtime experiments, extract from "discovery" onwards
            start_idx = full_key.find('discovery')
            if start_idx != -1:
                meaningful_part = full_key[start_idx:]
                # Remove trailing platform/version info like "_android_v3" -> keep just "discovery_realtime_v3"
                if '_android_' in meaningful_part:
                    # Keep version info but remove platform
                    parts = meaningful_part.split('_android_')
                    if len(parts) > 1:
                        meaningful_part = parts[0] + '_' + parts[1]  # discovery_realtime_v3
                elif '_ios_' in meaningful_part:
                    parts = meaningful_part.split('_ios_')
                    if len(parts) > 1:
                        meaningful_part = parts[0] + '_' + parts[1]
                
                # Convert to camelCase
                parts = meaningful_part.split('_')
                camel_case_key = parts[0] + ''.join(word.capitalize() for word in parts[1:])
            else:
                camel_case_key = full_key
        else:
            # Fallback: convert entire key to camelCase
            if '_' in full_key:
                parts = full_key.split('_')
                camel_case_key = parts[0] + ''.join(word.capitalize() for word in parts[1:])
            else:
                camel_case_key = full_key
        
        yaml_output = f"""{camel_case_key}:
  key: {values['key']}
  description: "{values['description']}"
  defaultValue: {values['defaultValue']}
  expiration: '{values['expiration']}'
  owner: {values['owner']}
  url: {values['url']}
  type: {values['type']}
  group: {values['group']}"""
        
        # Display in main Output tab
        self.yaml_output_display.delete(1.0, tk.END)
        self.yaml_output_display.insert(1.0, yaml_output)
        
        # Switch to the Output tab to show the result
        self.switch_to_output_tab()

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
            # Sync latest GUI values into in-memory config so requests use current entries
            if hasattr(self, 'config_vars') and isinstance(self.config_vars, dict):
                for key, var in self.config_vars.items():
                    try:
                        self.config[key] = var.get()
                    except Exception:
                        pass
            
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
            
            # Add cursor parameter if configured and not null
            cursor = self.config.get("CURSOR", "")
            if cursor and cursor.lower() != "null":
                params["cursor"] = cursor
            
            # Legacy: Also check if cursor exists in realtime events (for backward compatibility)
            realtime_events = self.config.get("REALTIME_EVENTS", "")
            if "cursor=" in realtime_events and not cursor:
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
            
            # Check if this is the experiments endpoint (requires POST with JSON body)
            if 'dynamic-values-edge-service' in self.config.get('API_BASE_URL', ''):
                # Experiments endpoint uses POST with JSON body
                headers["content-type"] = "application/json; charset=UTF-8"
                
                # Create the JSON body for experiments request
                json_body = {
                    "namespaces": [],
                    "legacy_namespaces": [],
                    "application": "consumer",
                    "app_version": "16.0.0-prod-debug",
                    "exposures_enabled": True,
                    "os": "Android",
                    "os_version": "16",
                    "context": {
                        "device_id": "78158b794698adba",
                        "device_region": "US",
                        "device_manufacturer": "Google",
                        "device_model": "sdk_gphone64_arm64",
                        "os_version": "36",
                        "language": "en",
                        "language_tag": "en-US",
                        "saved_info_user_id": "196174870",
                        "consumer_id": "195442085",
                        "submarket_id": self.config.get("SUBMARKET_ID", "1"),
                        "country_code": "US",
                        "is_guest": "false",
                        "team_id": "eef7656a-b0e1-4f34-a35e-4c3cc3f4a640",
                        "user_id": "196174870"
                    },
                    "dv_names": [
                        "mobile-feature-client-side-default",
                        "mobile-feature-multifeature-holdout",
                        "mobile-dv-telemetry-timeout-flag",
                        "mobile-feature-fetch-by-dv-list",
                        "android_async_dv_refresh_cutoff_time"
                    ],
                    "evaluation_options": {
                        "reference_exposure_enabled": True,
                        "client_side_default_enabled": False
                    }
                }
                
                # Make POST request with JSON body
                self.update_status("Making experiments API request (POST)...")
                response = requests.post(url, json=json_body, headers=headers, timeout=30)
            else:
                # Regular GET request for other endpoints
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
            self.experiments_display.delete('1.0', tk.END)
            self.update_status("Response cleared")
            
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
            
            # Display experiments analysis (if response contains experiments)
            if response_json and 'experiments' in response_json:
                experiments_analysis = self.parse_experiments_response(response_json)
                self.experiments_display.insert(tk.END, experiments_analysis)
                # Switch to experiments tab if experiments are found
                self.response_notebook.select(self.experiments_tab)
                experiments_count = len(response_json.get('experiments', []))
                self.update_status(f"✅ Request completed successfully - {experiments_count} experiments analyzed")
            else:
                # If no experiments, add a message to the experiments tab
                self.experiments_display.insert(tk.END, "🧪 EXPERIMENTS ANALYSIS\n" + "=" * 50 + "\n\n"
                                               + "❌ No experiments found in this response\n\n"
                                               + "This endpoint may not return experiment data, or\n"
                                               + "the response structure is different from expected.\n\n"
                                               + "Expected structure: {'experiments': [...]}")
                
                # Switch to the carousel titles tab to show results (fallback behavior)
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
            # Show enhanced JWT error dialog
            self.show_jwt_error_dialog("JWT Token Required", 
                                     "A JWT authorization token is required to make API requests.")
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
        instructions = ttk.Label(main_frame, text="""🔍 To get a JWT token:

Option 1: Create a test consumer (recommended)
• Go to DoorDash Dev Console and create a test account
• Use the generated JWT token from there

Option 2: Capture from existing requests
• Open Charles Proxy and capture DoorDash API requests
• Look for the 'authorization' header in any request  
• Copy ONLY the part after 'JWT ' (without the JWT prefix)

Example: authorization: JWT eyJhbGciOiJIUzI1NiJ9...
Copy: eyJhbGciOiJIUzI1NiJ9...

Paste your token below (JWT prefix will be automatically removed):""", 
                               justify=tk.LEFT, wraplength=500)
        instructions.pack(pady=(0, 15))
        
        # Dev Console button
        dev_console_frame = ttk.Frame(main_frame)
        dev_console_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(dev_console_frame, text="🌐 Open Dev Console", 
                  command=self.open_dev_console,
                  style='Accent.TButton').pack()
        
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
        self.experiments_display.delete('1.0', tk.END)
        self.update_status("Response cleared")
        
    def export_as_curl(self):
        """Export the current API request as a curl command"""
        try:
            # Validate auth token
            if not self.config.get('AUTHORIZATION_TOKEN'):
                self.show_jwt_error_dialog("Token Required for cURL Export", 
                                         "A JWT authorization token is required to generate the cURL command.")
                return
            
            # Build the same URL and parameters as make_request
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
            
            # Add cursor parameter if configured and not null
            cursor = self.config.get("CURSOR", "")
            if cursor and cursor.lower() != "null":
                params["cursor"] = cursor
            
            # Legacy: Also check if cursor exists in realtime events (for backward compatibility)
            realtime_events = self.config.get("REALTIME_EVENTS", "")
            if "cursor=" in realtime_events and not cursor:
                try:
                    import re
                    cursor_match = re.search(r'cursor=([^&\s]+)', realtime_events)
                    if cursor_match:
                        params["cursor"] = cursor_match.group(1)
                except:
                    pass
            
            # Build headers (same as make_request)
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
            
            # Build query string
            query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])
            full_url = f"{url}?{query_string}" if query_string else url
            
            # Check if this is the experiments endpoint (requires POST with JSON body)
            if 'dynamic-values-edge-service' in self.config.get('API_BASE_URL', ''):
                # Experiments endpoint uses POST with JSON body
                headers["content-type"] = "application/json; charset=UTF-8"
                
                # Create the JSON body for experiments request
                json_body = {
                    "namespaces": [],
                    "legacy_namespaces": [],
                    "application": "consumer",
                    "app_version": "16.0.0-prod-debug",
                    "exposures_enabled": True,
                    "os": "Android",
                    "os_version": "16",
                    "context": {
                        "device_id": "78158b794698adba",
                        "device_region": "US",
                        "device_manufacturer": "Google",
                        "device_model": "sdk_gphone64_arm64",
                        "os_version": "36",
                        "language": "en",
                        "language_tag": "en-US",
                        "saved_info_user_id": "196174870",
                        "consumer_id": "195442085",
                        "submarket_id": self.config.get("SUBMARKET_ID", "1"),
                        "country_code": "US",
                        "is_guest": "false",
                        "team_id": "eef7656a-b0e1-4f34-a35e-4c3cc3f4a640",
                        "user_id": "196174870"
                    },
                    "dv_names": [
                        "mobile-feature-client-side-default",
                        "mobile-feature-multifeature-holdout",
                        "mobile-dv-telemetry-timeout-flag",
                        "mobile-feature-fetch-by-dv-list",
                        "android_async_dv_refresh_cutoff_time"
                    ],
                    "evaluation_options": {
                        "reference_exposure_enabled": True,
                        "client_side_default_enabled": False
                    }
                }
                
                # Build curl command for POST request
                curl_cmd = f'curl -X POST "{url}" \\\n'
                for key, value in headers.items():
                    # Escape quotes in header values
                    escaped_value = value.replace('"', '\\"')
                    curl_cmd += f'  -H "{key}: {escaped_value}" \\\n'
                curl_cmd += f'  -d \'{json.dumps(json_body, indent=2)}\' \\\n'
                curl_cmd += f'  --compressed'
            else:
                # Build curl command for GET request
                curl_cmd = f'curl -X GET "{full_url}" \\\n'
                for key, value in headers.items():
                    # Escape quotes in header values
                    escaped_value = value.replace('"', '\\"')
                    curl_cmd += f'  -H "{key}: {escaped_value}" \\\n'
                curl_cmd += f'  --compressed'
            
            # Create a dialog to show the curl command
            self.show_curl_dialog(curl_cmd)
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate curl command: {str(e)}")
    
    def show_curl_dialog(self, curl_command):
        """Show curl command in a dialog with copy functionality"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 Export as cURL Command")
        dialog.geometry("800x600")
        dialog.resizable(True, True)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = ttk.Label(main_frame, text="📋 cURL Command", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Copy this command to run the API request from your terminal:",
                                font=('Arial', 10))
        instructions.pack(pady=(0, 10))
        
        # Text area with curl command
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        curl_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                            font=('Consolas', 10), height=20)
        curl_text.pack(fill=tk.BOTH, expand=True)
        curl_text.insert('1.0', curl_command)
        curl_text.config(state='normal')  # Keep editable so user can select/copy
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(curl_command)
            dialog.update()  # Required for clipboard to work
            messagebox.showinfo("Copied", "cURL command copied to clipboard!")
        
        def close_dialog():
            dialog.destroy()
        
        # Buttons
        ttk.Button(button_frame, text="📋 Copy to Clipboard", 
                  command=copy_to_clipboard, 
                  style='Accent.TButton').pack(side=tk.LEFT)
        ttk.Button(button_frame, text="❌ Close", 
                  command=close_dialog).pack(side=tk.RIGHT)
        
        # Bind Escape key to close
        dialog.bind('<Escape>', lambda e: close_dialog())
        
        # Focus on the text area for easy selection
        curl_text.focus_set()
        curl_text.tag_add(tk.SEL, "1.0", tk.END)  # Select all text
        
    def open_dev_console(self):
        """Open DoorDash Dev Console for creating test accounts and getting JWTs"""
        try:
            webbrowser.open("https://devconsole.doordash.team/test-studio/test-accounts")
        except Exception as e:
            messagebox.showerror("Browser Error", f"Failed to open Dev Console: {str(e)}")
    
    def show_jwt_error_dialog(self, title, message):
        """Show JWT error dialog with Dev Console and Set Token options"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (150)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text=f"🔑 {title}", 
                               font=('Arial', 14, 'bold'))
        title_label.pack()
        
        # Message
        message_label = ttk.Label(main_frame, text=message, 
                                 font=('Arial', 11), justify=tk.CENTER)
        message_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="💡 If you don't have a JWT token, you can create a test consumer account:", 
                                font=('Arial', 10), justify=tk.CENTER)
        instructions.pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def open_dev_console_and_close():
            self.open_dev_console()
            dialog.destroy()
        
        def set_token_and_close():
            dialog.destroy()
            self.set_auth_token()
        
        def close_dialog():
            dialog.destroy()
        
        # Dev Console button (primary action)
        ttk.Button(button_frame, text="🌐 Open Dev Console", 
                  command=open_dev_console_and_close,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        # Set Token button
        ttk.Button(button_frame, text="🔑 Set Existing Token", 
                  command=set_token_and_close).pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=close_dialog).pack(side=tk.RIGHT)
        
        # Bind Escape key to close
        dialog.bind('<Escape>', lambda e: close_dialog())
        
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
        preset_dialog.geometry("700x500")
        preset_dialog.transient(self.root)
        preset_dialog.grab_set()
        
        # Center the dialog
        preset_dialog.update_idletasks()
        x = (preset_dialog.winfo_screenwidth() // 2) - (350)
        y = (preset_dialog.winfo_screenheight() // 2) - (250)
        preset_dialog.geometry(f"700x500+{x}+{y}")
        
        # Main frame with more padding
        main_frame = ttk.Frame(preset_dialog, padding=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔧 API Configuration Presets", 
                               font=(self.choose_font_family(), 12, 'bold'))
        title_label.pack(pady=(0, 25))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Select a preset configuration to quickly set up API endpoints with all required headers and parameters.",
                              font=('Arial', 10), wraplength=650, justify=tk.CENTER)
        desc_label.pack(pady=(0, 30))
        
        # Preset selector frame with more padding
        selector_frame = ttk.LabelFrame(main_frame, text="Select Preset Configuration", padding=20)
        selector_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Dropdown with presets
        preset_label = ttk.Label(selector_frame, text="Available Presets:", font=('Arial', 11, 'bold'))
        preset_label.pack(anchor=tk.W, pady=(0, 15))
        
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
            },
            "🧪 Dynamic Values Edge Service - Experiments": {
                "description": "Feature flags and A/B testing endpoint with experiment configurations",
                "endpoint": "dynamic-values-edge-service.doordash.com/v1/experiments/",
                "method": self.apply_experiments_preset
            }
        }
        
        # Dropdown combobox
        self.selected_preset = tk.StringVar()
        preset_combo = ttk.Combobox(selector_frame, textvariable=self.selected_preset, 
                                   values=list(self.preset_options.keys()),
                                   state="readonly", width=80, font=('Arial', 10))
        preset_combo.pack(fill=tk.X, pady=(0, 20))
        preset_combo.set("Select a preset...")
        
        # Description area with more spacing
        desc_frame = ttk.Frame(selector_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(desc_frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.preset_desc_label = ttk.Label(desc_frame, text="Choose a preset to see its description", 
                                          font=('Arial', 9), wraplength=600, justify=tk.LEFT)
        self.preset_desc_label.pack(anchor=tk.W, pady=(8, 0))
        
        ttk.Label(desc_frame, text="Endpoint:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(15, 0))
        self.preset_endpoint_label = ttk.Label(desc_frame, text="", 
                                              font=('Consolas', 9), foreground='blue')
        self.preset_endpoint_label.pack(anchor=tk.W, pady=(8, 0))
        
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
            'REALTIME_EVENTS': '[{"action_type":"store_visit","entity_id":"4932","timestamp":"2025-08-07 12:47:57"}]',
            'CURSOR': 'eyJvZmZzZXQiOjAsImNvbnRlbnRfaWRzIjpbXSwicmVxdWVzdF9wYXJlbnRfaWQiOiIiLCJyZXF1ZXN0X2NoaWxkX2lkIjoiIiwicmVxdWVzdF9jaGlsZF9jb21wb25lbnRfaWQiOiIiLCJjcm9zc192ZXJ0aWNhbF9wYWdlX3R5cGUiOiJIT01FUEFHRSIsInBhZ2Vfc3RhY2tfdHJhY2UiOltdLCJ2ZXJ0aWNhbF9pZHMiOlsxMDMsMywyLDE3NCwzNywxMzksMTQ2LDEzNiw3MCwyNjgsMjQxLDIzNSwyMzYsMTEwMDAxLDQsMjM4LDI0MywyODIsMTEwMDE2LDEwMDMzM10sInZlcnRpY2FsX2NvbnRleHRfaWQiOm51bGwsImxheW91dF9vdmVycmlkZSI6IlVOU1BFQ0lGSUVEIiwic2luZ2xlX3N0b3JlX2lkIjpudWxsLCJzZWFyY2hfaXRlbV9jYXJvdXNlbF9jdXJzb3IiOm51bGwsImNhdGVnb3J5X2lkcyI6W10sImNvbGxlY3Rpb25faWRzIjpbXSwiZGRfcGxhY2VfaWRzIjpbImMyNjc5NjAzLTg4OGYtNDI0NC1iZTcxLTYzZDc5NmU4MGNiMCIsImQxYzRhZjBjLTJmNzMtNDljNC05YzkzLWM1OWE4YzMwODcyNSJdLCJuZXh0X3BhZ2VfY2FjaGVfa2V5IjoiVkVSVElDQUw6MTk1NDQyMDg1Ojc4MTU4Yjc5NDY5OGFkYmE6MTplN2E1YTAzMy1hZTA4LTQyY2MtODdjYi1iYzUxODM0MThmYTM6TFo0IiwiaXNfcGFnaW5hdGlvbl9mYWxsYmFjayI6bnVsbCwic291cmNlX3BhZ2VfdHlwZSI6bnVsbCwiZ2VvX3R5cGUiOiIiLCJnZW9faWQiOiIiLCJrZXl3b3JkIjoiIiwiYWRzX2N1cnNvcl9jYWNoZV9rZXkiOm51bGwsInZpc3VhbF9haXNsZXNfaW5zZXJ0aW9uX2luZGV4IjpudWxsLCJiYXNlQ3Vyc29yIjp7InBhZ2VfaWQiOiIiLCJwYWdlX3R5cGUiOiJOT1RfQVBQTElDQUJMRSIsImN1cnNvcl92ZXJzaW9uIjoiRkFDRVQifSwidmVydGljYWxfbmFtZXMiOnt9LCJpdGVtX2lkcyI6W10sIm1lcmNoYW50X3N1cHBsaWVkX2lkcyI6W10sImlzX291dF9vZl9zdG9jayI6bnVsbCwibWVudV9pZCI6bnVsbCwidHJhY2tpbmciOm51bGwsImRpZXRhcnlfdGFnIjpudWxsLCJvcmlnaW5fdGl0bGUiOm51bGwsInJhbmtlZF9yZW1haW5pbmdfY29sbGVjdGlvbl9pZHMiOm51bGwsInByZXZpb3VzbHlfc2Vlbl9jb2xsZWN0aW9uX2lkcyI6W10sInByZWNoZWNrb3V0X2J1bmRsZV9zZWFyY2hfaW5mbyI6bnVsbCwidG90YWxfaXRlbXNfb2Zmc2V0IjowLCJ0b3RhbF9hZHNfcHJldmlvdXNseV9ibGVuZGVkIjowLCJ2ZXJ0aWNhbF90aXRsZSI6bnVsbCwibXVsdGlfc3RvcmVfZW50aXRpZXMiOltdLCJjdXJzb3JWZXJzaW9uIjoiRkFDRVRfQ09OVEVOVF9PRkZTRVQiLCJwYWdlSWQiOiIiLCJwYWdlVHlwZSI6Ik5PVF9BUFBMSUNBQkxFIn0%3D',
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
            'REALTIME_EVENTS': '[]',
            'CURSOR': 'eyJvZmZzZXQiOjAsImNvbnRlbnRfaWRzIjpbXSwicmVxdWVzdF9wYXJlbnRfaWQiOiIiLCJyZXF1ZXN0X2NoaWxkX2lkIjoiIiwicmVxdWVzdF9jaGlsZF9jb21wb25lbnRfaWQiOiIiLCJjcm9zc192ZXJ0aWNhbF9wYWdlX3R5cGUiOiJIT01FUEFHRSIsInBhZ2Vfc3RhY2tfdHJhY2UiOltdLCJ2ZXJ0aWNhbF9pZHMiOlsxMDMsMywyLDE3NCwzNywxMzksMTQ2LDEzNiw3MCwyNjgsMjQxLDIzNSwyMzYsMTEwMDAxLDQsMjM4LDI0MywyODIsMTEwMDE2LDEwMDMzM10sInZlcnRpY2FsX2NvbnRleHRfaWQiOm51bGwsImxheW91dF9vdmVycmlkZSI6IlVOU1BFQ0lGSUVEIiwic2luZ2xlX3N0b3JlX2lkIjpudWxsLCJzZWFyY2hfaXRlbV9jYXJvdXNlbF9jdXJzb3IiOm51bGwsImNhdGVnb3J5X2lkcyI6W10sImNvbGxlY3Rpb25faWRzIjpbXSwiZGRfcGxhY2VfaWRzIjpbImMyNjc5NjAzLTg4OGYtNDI0NC1iZTcxLTYzZDc5NmU4MGNiMCIsImQxYzRhZjBjLTJmNzMtNDljNC05YzkzLWM1OWE4YzMwODcyNSJdLCJuZXh0X3BhZ2VfY2FjaGVfa2V5IjoiVkVSVElDQUw6MTk1NDQyMDg1OjEyMTFjNzMzMWQ1ZmZlMmY6MTo4MGZkNWFmMS0yOGZlLTQ3YzctYjljNS0zZTE2MGU1OGRhMmY6TFo0IiwiaXNfcGFnaW5hdGlvbl9mYWxsYmFjayI6bnVsbCwic291cmNlX3BhZ2VfdHlwZSI6bnVsbCwiZ2VvX3R5cGUiOiIiLCJnZW9faWQiOiIiLCJrZXl3b3JkIjoiIiwiYWRzX2N1cnNvcl9jYWNoZV9rZXkiOm51bGwsInZpc3VhbF9haXNsZXNfaW5zZXJ0aW9uX2luZGV4IjpudWxsLCJiYXNlQ3Vyc29yIjp7InBhZ2VfaWQiOiIiLCJwYWdlX3R5cGUiOiJOT1RfQVBQTElDQUJMRSIsImN1cnNvcl92ZXJzaW9uIjoiRkFDRVQifSwidmVydGljYWxfbmFtZXMiOnt9LCJpdGVtX2lkcyI6W10sIm1lcmNoYW50X3N1cHBsaWVkX2lkcyI6W10sImlzX291dF9vZl9zdG9jayI6bnVsbCwibWVudV9pZCI6bnVsbCwidHJhY2tpbmciOm51bGwsImRpZXRhcnlfdGFnIjpudWxsLCJvcmlnaW5fdGl0bGUiOm51bGwsInJhbmtlZF9yZW1haW5pbmdfY29sbGVjdGlvbl9pZHMiOm51bGwsInByZXZpb3VzbHlfc2Vlbl9jb2xsZWN0aW9uX2lkcyI6W10sInByZWNoZWNrb3V0X2J1bmRsZV9zZWFyY2hfaW5mbyI6bnVsbCwidG90YWxfaXRlbXNfb2Zmc2V0IjowLCJ0b3RhbF9hZHNfcHJldmlvdXNseV9ibGVuZGVkIjowLCJ2ZXJ0aWNhbF90aXRsZSI6bnVsbCwibXVsdGlfc3RvcmVfZW50aXRpZXMiOltdLCJjdXJzb3JWZXJzaW9uIjoiRkFDRVRfQ09OVEVOVF9PRkZTRVQiLCJwYWdlSWQiOiIiLCJwYWdlVHlwZSI6Ik5PVF9BUFBMSUNBQkxFIn0=',
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
    
    def apply_experiments_preset(self):
        """Apply the Dynamic Values Edge Service (Experiments) preset configuration"""
        experiments_config = {
            'API_BASE_URL': 'https://dynamic-values-edge-service.doordash.com',
            'API_ENDPOINT_PATH': '/v1/experiments/',
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
            'SESSION_ID': '4e978b72-6fe4-46bc-8ab1-bf4dc15f044a-dd-and',
            'CLIENT_REQUEST_ID': 'f2e5d745-6d07-4617-927a-bd7e9ef684e7-dd-and',
            'CORRELATION_ID': '3d682d82-3ee7-4340-b45a-ca5e61d5c472-dd-and',
            'DD_LOCATION_CONTEXT': 'eyJsYXQiOjM0LjAyODI5MDMsImxuZyI6LTExOC4zNzM0MjEsIm1hcmtldF9pZCI6IjIiLCJzdWJtYXJrZXRfaWQiOiIxIiwiZGlzdHJpY3RfaWQiOiIzIiwidGltZXpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiemlwY29kZSI6IjkwMDE2IiwiY291bnRyeV9zaG9ydF9uYW1lIjoiVVMiLCJjaXR5IjoiTG9zIEFuZ2VsZXMiLCJzdGF0ZSI6IkNBIiwiY29uc3VtZXJfYWRkcmVzc19saW5rX2lkIjoiMTQ1NTEyMzQxMiIsImFkZHJlc3NfaWQiOiIzNDUyMzM0MjkiLCJpc19ndWVzdF9jb25zdW1lciI6ZmFsc2V9',
            'DD_IDS': '{"dd_device_id":"78158b794698adba","dd_delivery_correlation_id":"6823d337-a3cf-4072-81b3-aa6fcba69b8d","dd_login_id":"lx_d16f81d2-773c-4f06-9997-b0de82bfbf32","dd_session_id":"sx_eb41331c-72f7-4b26-bba4-1e58f7ba6566","dd_android_id":"78158b794698adba","dd_android_advertising_id":"29804a87-b1f8-4db9-be15-a25ec4606c91"}',
            'COOKIE': '__cf_bm=_DHaY3P7NuK95vuimOfTDAeBOcpBYH3mHaZ6Ia9wX6s-1754600424-1.0.1.1-HhYoMjoYVDwBBmEPJlEeB9IH0OBHGz3meHRXhZ0_KIR0XKu6eCnm8BpKrK9uMAW5QYsvAHN0udFsYdTxhGwkw2IhJsiSjrn2_boP9AZzQHw; dd_country_shortname=US; dd_market_id=2',
            'REALTIME_EVENTS': '{}',  # This endpoint uses POST body instead
            'DEFAULT_VERBOSE': 'true',
            'MAX_VERBOSE_LINES': '100'
        }
        
        # Update config and GUI variables
        for key, value in experiments_config.items():
            self.config[key] = value
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        self.refresh_config_display()
        self.close_api_presets_modal()
        messagebox.showinfo("Preset Applied", 
                           "✅ Dynamic Values Edge Service (Experiments) configuration applied!\n\n" +
                           "This preset configures the experiments endpoint to fetch feature flags and A/B tests.")
    
    def apply_ios_prod_preset(self):
        """Apply iOS Production client configuration"""
        ios_config = {
            'USER_AGENT': 'DoordashConsumer/7.26.1 (iPhone; iOS 18.5; Scale/3.0)',
            'CLIENT_VERSION': 'ios v7.26.1'
        }
        
        # Update config dictionary
        for key, value in ios_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in ios_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        self.update_status("Applied iOS Production client configuration")
        messagebox.showinfo("iOS Prod Applied", 
                          "📱 iOS Production client configuration applied!\n\n"
                          "✅ User Agent: DoordashConsumer/7.26.1 (iPhone; iOS 18.5; Scale/3.0)\n"
                          "✅ Client Version: ios v7.26.1")
    
    def apply_android_prod_preset(self):
        """Apply Android Production client configuration"""
        android_config = {
            'USER_AGENT': 'DoorDashConsumer/Android 15.227.5',
            'CLIENT_VERSION': 'android v15.227.5'
        }
        
        # Update config dictionary
        for key, value in android_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in android_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        self.update_status("Applied Android Production client configuration")
        messagebox.showinfo("Android Prod Applied", 
                          "🤖 Android Production client configuration applied!\n\n"
                          "✅ User Agent: DoorDashConsumer/Android 15.227.5\n"
                          "✅ Client Version: android v15.227.5")
    
    def apply_android_debug_preset(self):
        """Apply Android Debug client configuration"""
        android_debug_config = {
            'USER_AGENT': 'DoorDashConsumer/Android 16.0.0-prod-debug',
            'CLIENT_VERSION': 'android v16.0.0-prod-debug b16000009'
        }
        
        # Update config dictionary
        for key, value in android_debug_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in android_debug_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        self.update_status("Applied Android Debug client configuration")
        messagebox.showinfo("Android Debug Applied", 
                          "🛠️ Android Debug client configuration applied!\n\n"
                          "✅ User Agent: DoorDashConsumer/Android 16.0.0-prod-debug\n"
                          "✅ Client Version: android v16.0.0-prod-debug b16000009")
    
    def apply_web_chrome_preset(self):
        """Apply Web Chrome client configuration"""
        web_chrome_config = {
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'CLIENT_VERSION': ''
        }
        
        # Update config dictionary
        for key, value in web_chrome_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in web_chrome_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        self.update_status("Applied Web Chrome client configuration")
        messagebox.showinfo("Web Chrome Applied", 
                          "🌐 Web Chrome client configuration applied!\n\n"
                          "✅ User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36\n"
                          "✅ Client Version: (cleared)")
    
    def apply_sf_office_preset(self):
        """Apply SF Office location configuration"""
        sf_office_config = {
            'LATITUDE': '37.78511',
            'LONGITUDE': '-122.39574'
        }
        
        # Update config dictionary
        for key, value in sf_office_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in sf_office_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        self.update_status("Applied SF Office location configuration")
        messagebox.showinfo("SF Office Applied", 
                          "🏢 SF Office location configuration applied!\n\n"
                          "📍 Address: 303 2nd Street, Suite 800, San Francisco CA\n"
                          "🗺️ Location: Marathon Plaza\n"
                          "✅ Latitude: 37.78511° N\n"
                          "✅ Longitude: -122.39574° W")
    
    def apply_ny_office_preset(self):
        """Apply NY Office location configuration"""
        ny_office_config = {
            'LATITUDE': '40.7410',
            'LONGITUDE': '-73.9902'
        }
        
        # Update config dictionary
        for key, value in ny_office_config.items():
            self.config[key] = value
            
        # Update GUI variables
        for key, value in ny_office_config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
        
        self.update_status("Applied NY Office location configuration")
        messagebox.showinfo("NY Office Applied", 
                          "🗽 NY Office location configuration applied!\n\n"
                          "📍 Address: 200 5th Avenue, New York, NY 10010\n"
                          "🗺️ Location: Flatiron District\n"
                          "✅ Latitude: 40.7410° N\n"
                          "✅ Longitude: -73.9902° W")
    
    def parse_experiments_response(self, response_data):
        """Parse experiments response and format for display"""
        try:
            if not isinstance(response_data, dict):
                return "⚠️ Response is not in expected JSON format"
            
            experiments = response_data.get('experiments', [])
            if not experiments:
                return "⚠️ No experiments found in response"
            
            result = []
            result.append("🧪 EXPERIMENTS ANALYSIS")
            result.append("=" * 50)
            result.append(f"📊 Total Experiments: {len(experiments)}")
            result.append("")
            
            treatment_count = 0
            control_count = 0
            other_count = 0
            
            for i, exp in enumerate(experiments, 1):
                name = exp.get('name', 'Unknown')
                value = exp.get('value', 'N/A')
                exposure_enabled = exp.get('exposure_enabled', False)
                exposure_context = exp.get('exposure_context', {})
                
                result.append(f"🔬 Experiment #{i}: {name}")
                result.append(f"   💡 Value: {value}")
                result.append(f"   📈 Exposure Enabled: {exposure_enabled}")
                
                if exposure_context:
                    tag = exposure_context.get('tag', 'unknown')
                    distribution = exposure_context.get('distribution', 'unknown')
                    segment = exposure_context.get('segment', 'unknown')
                    bucket_key = exposure_context.get('bucket_key', 'unknown')
                    
                    result.append(f"   🎯 Assignment: {tag}")
                    result.append(f"   📋 Distribution: {distribution}")
                    result.append(f"   👥 Segment: {segment}")
                    result.append(f"   🔑 Bucket Key: {bucket_key}")
                    
                    # Count assignments
                    if 'treatment' in tag.lower():
                        treatment_count += 1
                    elif 'control' in tag.lower():
                        control_count += 1
                    else:
                        other_count += 1
                else:
                    # If no exposure context, check the value for assignment
                    value_str = str(value).lower()
                    if value_str in ['true', 'treatment', 'treatment1', 'treatment2', 'treatment3']:
                        treatment_count += 1
                        result.append(f"   🎯 Assignment: treatment (inferred from value)")
                    elif value_str in ['false', 'control']:
                        control_count += 1
                        result.append(f"   🎯 Assignment: control (inferred from value)")
                    else:
                        other_count += 1
                        result.append(f"   🎯 Assignment: {value} (other)")
                
                result.append("")
            
            # Summary section
            result.append("📈 ASSIGNMENT SUMMARY")
            result.append("=" * 25)
            result.append(f"🟢 Treatment Variants: {treatment_count}")
            result.append(f"🔵 Control Variants: {control_count}")
            result.append(f"🟡 Other Assignments: {other_count}")
            result.append("")
            result.append(f"📊 Treatment Rate: {treatment_count}/{len(experiments)} ({(treatment_count/len(experiments)*100):.1f}%)")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error parsing experiments: {str(e)}"
    
    def extract_carousel_titles(self, response_data):
        """Extract carousel titles from store_carousel components in nested JSON structure"""
        carousels = []
        try:
            if response_data:
                # Recursively search through the entire JSON structure
                self.find_store_carousels_recursive(response_data, carousels)
                            
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

    def create_actions_sidebar(self, parent):
        """Create a right-hand sidebar with always-visible actions and auth/info"""
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Actions
        actions = ttk.LabelFrame(container, text="Actions", padding=10)
        actions.pack(fill=tk.X)
        
        self.make_request_btn = ttk.Button(actions, text="Make Request", 
                                          command=self.make_request_threaded, style='Accent.TButton')
        self.make_request_btn.pack(fill=tk.X)
        
        ttk.Button(actions, text="Clear Response", command=self.clear_response).pack(fill=tk.X, pady=(8,0))
        ttk.Button(actions, text="Export as cURL", command=self.export_as_curl).pack(fill=tk.X, pady=(8,0))
        
        self.verbose_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(actions, text="Show detailed response", variable=self.verbose_var).pack(anchor='w', pady=(8,0))
        
        # Config actions
        cfg_actions = ttk.LabelFrame(container, text="Configuration", padding=10)
        cfg_actions.pack(fill=tk.X, pady=(12,0))
        ttk.Button(cfg_actions, text="💾 Save Configuration", command=self.save_configuration).pack(fill=tk.X)
        ttk.Button(cfg_actions, text="🔄 Reset to File", command=self.reset_configuration).pack(fill=tk.X, pady=(8,0))
        ttk.Button(cfg_actions, text="📁 Save to File", command=self.save_to_file).pack(fill=tk.X, pady=(0,0))
        
        # Divider
        ttk.Separator(container, orient='horizontal').pack(fill=tk.X, pady=12)
        
        # Authentication quick section
        auth = ttk.LabelFrame(container, text="Authentication", padding=10)
        auth.pack(fill=tk.X)
        
        token_var = self.config_vars.get('AUTHORIZATION_TOKEN') if hasattr(self, 'config_vars') else None
        if token_var is None:
            token_var = tk.StringVar(value=self.config.get('AUTHORIZATION_TOKEN', '') or '')
            if hasattr(self, 'config_vars'):
                self.config_vars['AUTHORIZATION_TOKEN'] = token_var
        
        ttk.Label(auth, text="Authorization Token:").pack(anchor='w')
        ttk.Entry(auth, textvariable=token_var, show="", width=48).pack(fill=tk.X)
        ttk.Button(auth, text="🔍 Fetch from Android Logs", command=self.open_fetch_auth_from_android_modal).pack(fill=tk.X, pady=(8,0))
        
        # Client Info quick section
        client = ttk.LabelFrame(container, text="Client Info", padding=10)
        client.pack(fill=tk.BOTH, expand=True, pady=(12,0))
        
        ua_var = self.config_vars.get('USER_AGENT') if hasattr(self, 'config_vars') else None
        if ua_var is None:
            ua_var = tk.StringVar(value=self.config.get('USER_AGENT',''))
            if hasattr(self, 'config_vars'):
                self.config_vars['USER_AGENT'] = ua_var
        
        cv_var = self.config_vars.get('CLIENT_VERSION') if hasattr(self, 'config_vars') else None
        if cv_var is None:
            cv_var = tk.StringVar(value=self.config.get('CLIENT_VERSION',''))
            if hasattr(self, 'config_vars'):
                self.config_vars['CLIENT_VERSION'] = cv_var
        
        ttk.Label(client, text="User Agent:").pack(anchor='w')
        ttk.Entry(client, textvariable=ua_var).pack(fill=tk.X)
        ttk.Label(client, text="Client Version:").pack(anchor='w', pady=(8,0))
        ttk.Entry(client, textvariable=cv_var).pack(fill=tk.X)
        
        ttk.Label(client, text="Tip: Full settings available on the left tabs.", foreground='gray').pack(anchor='w', pady=(10,0))

    def setup_android_emulator(self):
        """Set up and start an Android emulator with Charles Proxy configuration"""
        try:
            self.proxy_status_var.set("Setting up Android emulator...")
            self.root.update_idletasks()
            
            # Get proxy settings from GUI
            proxy_url = self.config_vars.get('CHARLES_PROXY_URL', tk.StringVar(value='127.0.0.1')).get()
            proxy_port = self.config_vars.get('CHARLES_PROXY_PORT', tk.StringVar(value='8888')).get()
            avd_name = self.config_vars.get('ANDROID_AVD_NAME', tk.StringVar(value='Pixel_9_Pro_-_Charles')).get()
            
            if not proxy_url or not proxy_port:
                self.proxy_status_var.set("Error: Please set proxy URL and port")
                return
            
            if not avd_name:
                self.proxy_status_var.set("Error: Please set AVD name")
                return
            
            # Run emulator setup in a separate thread
            threading.Thread(target=self._setup_emulator_threaded, 
                           args=(proxy_url, proxy_port, avd_name), daemon=True).start()
            
        except Exception as e:
            self.proxy_status_var.set(f"Error: {str(e)}")
            print(f"Error setting up emulator: {e}")

    def auto_detect_avd(self):
        """Auto-detect available AVDs and suggest the best one for Charles Proxy"""
        try:
            self.proxy_status_var.set("Auto-detecting AVDs...")
            self.root.update_idletasks()
            
            # Find emulator command
            emulator_path = self._find_emulator()
            if not emulator_path:
                self.proxy_status_var.set("Error: Android emulator not found")
                return
            
            # List AVDs
            try:
                result = subprocess.run([emulator_path, '-list-avds'], 
                                     capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    avd_list = result.stdout.strip().split('\n')
                    
                    # Look for Charles-specific AVD first
                    charles_avd = None
                    for avd in avd_list:
                        if 'charles' in avd.lower():
                            charles_avd = avd
                            break
                    
                    if charles_avd:
                        self.config_vars['ANDROID_AVD_NAME'].set(charles_avd)
                        self.proxy_status_var.set(f"✅ Found perfect AVD: {charles_avd}")
                    elif avd_list:
                        self.config_vars['ANDROID_AVD_NAME'].set(avd_list[0])
                        self.proxy_status_var.set(f"✅ Using AVD: {avd_list[0]}")
                    else:
                        self.proxy_status_var.set("No AVDs found")
                        
                else:
                    self.proxy_status_var.set("No AVDs found")
                    
            except Exception as e:
                self.proxy_status_var.set(f"Error detecting AVDs: {str(e)}")
                
        except Exception as e:
            self.proxy_status_var.set(f"Error: {str(e)}")
            print(f"Error auto-detecting AVD: {e}")

    def _find_emulator(self):
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

    def _setup_emulator_threaded(self, proxy_url, proxy_port, avd_name):
        """Threaded method to set up the emulator"""
        try:
            # Find adb
            adb_path = self._find_adb()
            if not adb_path:
                self.proxy_status_var.set("Error: ADB not found. Install Android Platform-Tools")
                return
            
            # Check if AVD exists
            emulator_path = self._find_emulator()
            if not emulator_path:
                self.proxy_status_var.set("Error: Android emulator not found. Install Android SDK")
                return
            
            # List available AVDs to verify
            try:
                result = subprocess.run([emulator_path, '-list-avds'], 
                                     capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    available_avds = result.stdout.strip().split('\n')
                    if avd_name not in available_avds:
                        self.proxy_status_var.set(f"Error: AVD '{avd_name}' not found. Available: {', '.join(available_avds)}")
                        return
                else:
                    self.proxy_status_var.set("Error: Cannot list AVDs")
                    return
            except Exception as e:
                self.proxy_status_var.set(f"Error listing AVDs: {str(e)}")
                return
            
            # Start emulator
            self.proxy_status_var.set(f"Starting emulator: {avd_name}")
            self.root.update_idletasks()
            
            # Start emulator with proxy settings
            emulator_cmd = [
                emulator_path, '-avd', avd_name, 
                '-http-proxy', f'{proxy_url}:{proxy_port}',
                '-no-snapshot-load',
                '-no-boot-anim',  # Faster boot
                '-gpu', 'swiftshader_indirect',  # Software rendering
                '-memory', '2048',  # 2GB RAM
                '-cores', '2'  # 2 CPU cores
            ]
            
            try:
                # Start emulator in background
                process = subprocess.Popen(emulator_cmd, 
                                        cwd=os.path.dirname(emulator_path),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                
                self.proxy_status_var.set(f"Emulator started! PID: {process.pid}")
                self.root.update_idletasks()
                
                # Wait for device to be ready
                if self._wait_for_device(adb_path):
                    self.proxy_status_var.set("Device ready! Configuring proxy...")
                    self.root.update_idletasks()
                    
                    # Configure proxy on the device
                    self._configure_device_proxy(adb_path, proxy_url, proxy_port)
                else:
                    self.proxy_status_var.set("Device not ready within timeout")
                    
            except Exception as e:
                self.proxy_status_var.set(f"Error starting emulator: {str(e)}")
                
        except Exception as e:
            self.proxy_status_var.set(f"Error: {str(e)}")
            print(f"Error in emulator setup: {e}")

    def _wait_for_device(self, adb_path, timeout=120):
        """Wait for the emulator device to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run([adb_path, 'wait-for-device'], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return True
            except subprocess.TimeoutExpired:
                pass
            
            # Check if device is listed
            try:
                result = subprocess.run([adb_path, 'devices'], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and 'device' in result.stdout:
                    return True
            except subprocess.TimeoutExpired:
                pass
            
            time.sleep(5)
        
        return False

    def _configure_device_proxy(self, adb_path, proxy_url, proxy_port, device_id=None):
        """Configure proxy settings on the Android device"""
        try:
            # Build adb command with optional device targeting
            adb_cmd = [adb_path]
            if device_id:
                adb_cmd.extend(['-s', device_id])
            
            # Wait for device to be ready
            result = subprocess.run(adb_cmd + ['wait-for-device'], capture_output=True, text=True)
            if result.returncode != 0:
                self.proxy_status_var.set("Error: Device not ready")
                return
            
            # Set proxy using Android settings
            proxy_settings = f"{proxy_url}:{proxy_port}"
            
            # Method 1: Try using Android settings database
            try:
                subprocess.run(adb_cmd + ['shell', 'settings', 'put', 'global', 'http_proxy', proxy_settings], 
                             capture_output=True, text=True)
                self.proxy_status_var.set(f"Proxy configured: {proxy_settings}")
            except:
                # Method 2: Try using iptables (requires root)
                try:
                    subprocess.run(adb_cmd + ['shell', 'su', '-c', f'iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination {proxy_url}:{proxy_port}'], 
                                 capture_output=True, text=True)
                    subprocess.run(adb_cmd + ['shell', 'su', '-c', f'iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination {proxy_url}:{proxy_port}'], 
                                 capture_output=True, text=True)
                    self.proxy_status_var.set(f"Proxy configured via iptables: {proxy_settings}")
                except:
                    self.proxy_status_var.set("Proxy configured. Manual setup may be required in device settings")
            
        except Exception as e:
            self.proxy_status_var.set(f"Error configuring proxy: {str(e)}")

    def list_android_emulators(self):
        """List available Android emulators"""
        try:
            self.proxy_status_var.set("Listing available emulators...")
            self.root.update_idletasks()
            
            # Find emulator command
            emulator_path = shutil.which('emulator')
            if not emulator_path:
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
                        emulator_path = path
                        break
            
            if emulator_path:
                # List AVDs
                result = subprocess.run([emulator_path, '-list-avds'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    avd_list = result.stdout.strip().split('\n')
                    self.proxy_status_var.set(f"Found {len(avd_list)} emulator(s): {', '.join(avd_list)}")
                else:
                    self.proxy_status_var.set("No emulators found. Create one first.")
            else:
                self.proxy_status_var.set("Android emulator not found. Install Android SDK")
                
        except Exception as e:
            self.proxy_status_var.set(f"Error listing emulators: {str(e)}")

    def configure_proxy_on_device(self):
        """Configure proxy on currently connected device"""
        try:
            proxy_url = self.config_vars.get('CHARLES_PROXY_URL', tk.StringVar(value='127.0.0.1')).get()
            proxy_port = self.config_vars.get('CHARLES_PROXY_PORT', tk.StringVar(value='8888')).get()
            avd_name = self.config_vars.get('ANDROID_AVD_NAME', tk.StringVar(value='Pixel_9_Pro_-_Charles')).get()
            
            if not proxy_url or not proxy_port:
                self.proxy_status_var.set("Error: Please set proxy URL and port")
                return
            
            # Find adb
            adb_path = self._find_adb()
            if not adb_path:
                self.proxy_status_var.set("Error: ADB not found. Install Android Platform-Tools")
                return
            
            # Check if device is connected
            result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True)
            if result.returncode != 0:
                self.proxy_status_var.set("Error: ADB not responding")
                return
            
            if 'device' not in result.stdout:
                self.proxy_status_var.set("No Android device connected")
                return
            
            # If multiple devices, try to target the specific AVD
            devices = []
            for line in result.stdout.split('\n'):
                if '\tdevice' in line:
                    device_id = line.split('\t')[0]
                    devices.append(device_id)
            
            if len(devices) > 1:
                # Try to find the emulator with our AVD name
                target_device = None
                for device_id in devices:
                    try:
                        # Get device properties
                        prop_result = subprocess.run([adb_path, '-s', device_id, 'shell', 'getprop', 'ro.product.model'], 
                                                  capture_output=True, text=True, timeout=10)
                        if prop_result.returncode == 0 and avd_name.lower() in prop_result.stdout.lower():
                            target_device = device_id
                            break
                    except:
                        pass
                
                if target_device:
                    self.proxy_status_var.set(f"Targeting device: {target_device}")
                    # Configure proxy on specific device
                    self._configure_device_proxy(adb_path, proxy_url, proxy_port, target_device)
                else:
                    self.proxy_status_var.set("Multiple devices found. Please specify target device.")
            else:
                # Single device, configure normally
                self._configure_device_proxy(adb_path, proxy_url, proxy_port)
            
        except Exception as e:
            self.proxy_status_var.set(f"Error: {str(e)}")

    def _find_adb(self):
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

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run the application
    app = DoorDashAPIGUI(root)
    
    # Center and bring to front to ensure it is visible
    try:
        root.update_idletasks()
        root.eval('tk::PlaceWindow . center')
        root.deiconify()
        root.lift()
        root.attributes('-topmost', True)
        root.after(600, lambda: root.attributes('-topmost', False))
    except Exception:
        pass
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main() 