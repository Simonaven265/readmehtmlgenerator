import markdown
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from markdown.extensions import fenced_code, codehilite
import webbrowser
import tempfile
from tkinter.ttk import Progressbar
import threading
import json
import base64
from urllib.parse import urljoin
from tkinter import colorchooser
from datetime import datetime
import gettext
import math
import re

# Set up translation
localedir = Path(__file__).parent / 'locales'
gettext.bindtextdomain('messages', localedir)
gettext.textdomain('messages')
_ = gettext.gettext

# Modern dark theme color scheme
COLORS = {
    'primary': '#2b3d4f',
    'primary_light': '#3d5a7a',
    'primary_dark': '#1a2530',
    'secondary': '#00b4d8',
    'secondary_light': '#48cae4',
    'accent': '#00e5ff',
    'background': '#1a1a1a',
    'surface': '#2d2d2d',
    'text': '#e0e0e0',  
    'text_light': '#b0b0b0', 
    'border': '#404040',
    'success': '#2dd4bf',
    'warning': '#fbbf24',
    'error': '#ef4444' 
}

class ModernUI:
    """Utility class with modern UI styling methods"""
    @staticmethod
    def configure_styles():
        style = ttk.Style()
        
        # Frame styling - dark
        style.configure('TFrame', background=COLORS['background'])
        style.configure('Surface.TFrame', background=COLORS['surface'])
        
        # Button styling - dark modern look
        style.configure('TButton', 
                      background=COLORS['primary'],
                      foreground=COLORS['text'],
                      padding=(15, 8),
                      font=('Segoe UI', 10),
                      borderwidth=0)
        style.map('TButton',
                background=[('active', COLORS['primary_light']), 
                           ('pressed', COLORS['primary_dark'])])
        
        # Primary button with bright accent
        style.configure('Primary.TButton', 
                      background=COLORS['secondary'],
                      foreground=COLORS['text'])
        style.map('Primary.TButton',
                background=[('active', COLORS['secondary_light']),
                           ('pressed', COLORS['secondary'])])
        
        # Accent button
        style.configure('Accent.TButton', 
                      background=COLORS['accent'],
                      foreground=COLORS['primary_dark'])
        
        # Label styling - light text on dark
        style.configure('TLabel', 
                      background=COLORS['background'],
                      foreground=COLORS['text'],
                      font=('Segoe UI', 10))
        
        # Header label with accent color
        style.configure('Header.TLabel', 
                      font=('Segoe UI', 24, 'bold'),
                      foreground=COLORS['secondary'])
        
        # Subheader label
        style.configure('Subheader.TLabel', 
                      font=('Segoe UI', 14),
                      foreground=COLORS['text_light'])
        
        # Entry styling for dark theme
        style.configure('TEntry', 
                      background=COLORS['surface'],
                      foreground=COLORS['text'],
                      fieldbackground=COLORS['surface'],
                      insertcolor=COLORS['text'],
                      padding=8,
                      font=('Segoe UI', 10))
        
        # Checkbutton with light text
        style.configure('TCheckbutton', 
                      background=COLORS['background'],
                      foreground=COLORS['text'],
                      font=('Segoe UI', 10))
        
        # Progressbar with bright accent
        style.configure('TProgressbar', 
                      background=COLORS['secondary'],
                      troughcolor=COLORS['surface'])
                      
        # Custom dropdown styling for dark theme
        style.configure('Dropdown.TMenubutton',
                     background=COLORS['surface'],
                     foreground=COLORS['text'],
                     padding=(10, 5),
                     font=('Segoe UI', 10))
        style.map('Dropdown.TMenubutton',
                background=[('active', COLORS['primary_light']),
                           ('pressed', COLORS['primary'])])

    @staticmethod
    def create_custom_button(parent, text, command, **kwargs):
        """Create a modern custom button with hover effects"""
        frame = tk.Frame(parent, background=COLORS['background'])
        
        btn = tk.Button(frame, text=text, command=command,
                     font=('Segoe UI', 10),
                     bg=COLORS['secondary'],
                     fg='white',
                     activebackground=COLORS['secondary_light'],
                     activeforeground='white',
                     bd=0,
                     padx=15,
                     pady=8,
                     cursor='hand2',
                     relief='flat',
                     **kwargs)
        
        def on_enter(e):
            btn['background'] = COLORS['secondary_light']
            
        def on_leave(e):
            btn['background'] = COLORS['secondary']
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.pack(padx=1, pady=1)
        
        return frame

# Initialize modern UI styles
ModernUI.configure_styles()

class ExportSettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.metadata = {
            'author': tk.StringVar(master=self),
            'description': tk.StringVar(master=self),
            'keywords': tk.StringVar(master=self),
        }
        
        self.title(_("Export Settings"))
        self.geometry("500x400")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Filename pattern tab
        filename_frame = ttk.Frame(notebook)
        notebook.add(filename_frame, text=_('Filename'))
        
        ttk.Label(filename_frame, text=_("Filename Pattern:")).pack(anchor='w', pady=5)
        self.pattern_var = tk.StringVar(master=self, value="{name}")
        pattern_entry = ttk.Entry(filename_frame, textvariable=self.pattern_var, width=40)
        pattern_entry.pack(fill='x', padx=5)

class ReadmeConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(_("README HTML Generator"))
        self.geometry("800x600")
        self.configure(bg=COLORS['background'])
        
        # Initialize state variables
        self.output_dir = None
        self.temp_preview_file = None
        self.cancel_conversion = False
        self.recent_files = self.load_preferences().get('recent_files', [])
        self.max_recent_files = 5
        
        # Create main container
        self.main_container = ttk.Frame(self, style='Surface.TFrame')
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create header
        header_label = ttk.Label(
            self.main_container,
            text=_("README HTML Generator"),
            style='Header.TLabel'
        )
        header_label.pack(pady=(0, 20))
        
        # Create file list
        self.files_frame = ttk.Frame(self.main_container)
        self.files_frame.pack(fill='both', expand=True, pady=10)
        
        self.files_text = tk.Text(
            self.files_frame,
            height=10,
            width=50,
            font=('Segoe UI', 10),
            bg=COLORS['surface'],
            fg=COLORS['text'],
            insertbackground=COLORS['text'],  # Cursor color
            selectbackground=COLORS['primary_light'],  # Selection background
            selectforeground=COLORS['text'],  # Selection text color
            relief='flat',  # Remove border
            padx=10,  # Add horizontal padding
            pady=10   # Add vertical padding
        )
        self.files_text.pack(fill='both', expand=True)
        
        # Enable drag and drop
        self.files_text.drop_target_register(DND_FILES)
        self.files_text.dnd_bind('<<Drop>>', self.on_drop)
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.main_container)
        self.buttons_frame.pack(fill='x', pady=20)
        
        # Add buttons
        browse_btn = ModernUI.create_custom_button(
            self.buttons_frame,
            _("Browse Files"),
            self.browse_files
        )
        browse_btn.pack(side='left', padx=5)
        
        convert_btn = ModernUI.create_custom_button(
            self.buttons_frame,
            _("Convert to HTML"),
            self.convert_files
        )
        convert_btn.pack(side='left', padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_container,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='TProgressbar'
        )
        self.progress_bar.pack(fill='x', pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_container,
            text="",
            style='TLabel'
        )
        self.status_label.pack(pady=5)
        
        # Create menu
        self.create_menu()
        
    def create_menu(self):
        """Create the main menu bar"""
        self.menu_bar = tk.Menu(self, bg=COLORS['surface'], fg=COLORS['text'])
        self.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(
            self.menu_bar,
            tearoff=0,
            bg=COLORS['surface'],
            fg=COLORS['text'],
            activebackground=COLORS['primary_light'],
            activeforeground=COLORS['text']
        )
        self.menu_bar.add_cascade(label=_("File"), menu=self.file_menu)
        self.file_menu.add_command(label=_("Open..."), command=self.browse_files)
        self.file_menu.add_command(label=_("Export Settings..."), command=self.show_export_settings)
        self.file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(
            self.file_menu,
            tearoff=0,
            bg=COLORS['surface'],
            fg=COLORS['text'],
            activebackground=COLORS['primary_light'],
            activeforeground=COLORS['text']
        )
        self.file_menu.add_cascade(label=_("Recent Files"), menu=self.recent_menu)
        self.update_recent_menu()
        
        self.file_menu.add_separator()
        self.file_menu.add_command(label=_("Exit"), command=self.quit)
        
        # Options menu
        options_menu = tk.Menu(
            self.menu_bar,
            tearoff=0,
            bg=COLORS['surface'],
            fg=COLORS['text'],
            activebackground=COLORS['primary_light'],
            activeforeground=COLORS['text']
        )
        self.menu_bar.add_cascade(label=_("Options"), menu=options_menu)
        options_menu.add_command(label=_("Export Options..."), command=self.show_export_options)
        options_menu.add_command(label=_("Theme Settings..."), command=self.show_theme_settings)
    
    def load_preferences(self):
        """Load user preferences from JSON file or create defaults"""
        default_preferences = {
            "recent_files": [],
            "current_theme": "default",
            "custom_themes": {},
            "export_options": {
                "mobile": False,
                "print": False,
                "toc": True
            },
            "export_settings": {
                "filename_pattern": "{name}",
                "metadata": {
                    "author": "",
                    "description": "",
                    "keywords": ""
                }
            }
        }

        try:
            with open('preferences.json', 'r') as f:
                prefs = json.load(f)

                # Ensure no local paths are included in recent_files
                prefs['recent_files'] = [
                    file for file in prefs.get('recent_files', [])
                    if os.path.exists(file)
                ]

                return prefs
        except (FileNotFoundError, json.JSONDecodeError):
            # Save default preferences if file is missing or corrupted
            self.save_preferences(default_preferences)
            return default_preferences
    
    def save_preferences(self, prefs):
        """Save user preferences to JSON file"""
        with open('preferences.json', 'w') as f:
            json.dump(prefs, f, indent=2)
    
    def browse_files(self):
        """Open file browser dialog"""
        files = filedialog.askopenfilenames(
            title=_("Select README files"),
            filetypes=[
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ]
        )
        if files:
            self.add_files(files)
    
    def add_files(self, files):
        """Add files to the list"""
        current = self.files_text.get("1.0", tk.END).strip()
        new_files = "\n".join(files)
        if current:
            self.files_text.insert(tk.END, f"\n{new_files}")
        else:
            self.files_text.insert("1.0", new_files)
        
        # Add to recent files
        self.add_to_recent_files(files)
    
    def on_drop(self, event):
        """Handle drag and drop events"""
        files = self.tk.splitlist(event.data)
        self.add_files(files)
    
    def convert_files(self):
        """Convert all files in the list"""
        files = self.files_text.get("1.0", tk.END).strip().split("\n")
        if not files or not files[0]:
            messagebox.showwarning(
                _("No Files"),
                _("Please add some README files to convert.")
            )
            return
        
        # Ask for output directory
        output_dir = filedialog.askdirectory(
            title=_("Select Output Directory")
        )
        if not output_dir:
            return
            
        self.output_dir = output_dir
        total_files = len(files)
        
        def update_progress(i, filename=""):
            """Update progress from main thread"""
            progress = (i / total_files) * 100
            self.progress_var.set(progress)
            self.status_label.config(
                text=_("Converting: {} ({}/{})").format(
                    filename, i, total_files
                )
            )
            self.update()

        def conversion_task():
            for i, file in enumerate(files, 1):
                if self.cancel_conversion:
                    break
                    
                try:
                    self.convert_readme_to_html(file)
                    # Schedule GUI updates in main thread
                    self.after(0, update_progress, i, Path(file).name)
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror(
                        _("Error"),
                        _("Error converting {}: {}").format(file, str(e))
                    ))
            
            def finish_conversion():
                self.status_label.config(text=_("Conversion complete!"))
                self.progress_var.set(0)
                self.cancel_conversion = False
                
                # Ask to open output directory
                if messagebox.askyesno(
                    _("Complete"),
                    _("Conversion complete! Would you like to open the output directory?")
                ):
                    self.open_output_dir()
            
            # Schedule completion in main thread
            self.after(0, finish_conversion)
        
        # Run conversion in background thread
        self.cancel_conversion = False
        threading.Thread(target=conversion_task, daemon=True).start()
    
    def convert_readme_to_html(self, readme_path, output_dir=None, preview_mode=False):
        """Convert a README file to HTML"""
        # Read markdown content
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML
        html = markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'codehilite',
                'tables',
                'toc'
            ]
        )
        
        # Apply template
        css = self.get_theme_css()
        template = self.get_html_template()
        filename = Path(readme_path).stem
        
        html_template = template.format(
            title=filename,
            content=html,
            css=css,
            js=self.get_theme_js()
        )
        
        if preview_mode:
            return html_template
        
        # Generate output path and write file
        output_path = Path(readme_path).with_suffix('').with_name(filename + '.html')
        if output_dir:
            output_path = Path(output_dir) / output_path.name
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return output_path
    
    def get_theme_css(self):
        """Get theme CSS including custom styles"""
        with open('styles.css', 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_theme_js(self):
        """Get theme JavaScript"""
        return """
        // Theme toggler
        function toggleDarkMode() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-theme'));
        }
        
        // Check for saved theme preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-theme');
        }
        
        // Add theme toggle button
        const themeToggle = document.createElement('div');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = `
            <button onclick="toggleDarkMode()">Toggle Theme</button>
        `;
        document.body.appendChild(themeToggle);
        """
    
    def get_html_template(self):
        """Get HTML template"""
        return """<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{title}</title>
            <style>{css}</style>
        </head>
        <body class="mode-transition">
            <div class="content">
                {content}
            </div>
            <script>{js}</script>
        </body>
        </html>"""
    
    def show_export_options(self):
        """Show export options dialog"""
        dialog = ExportOptionsDialog(self)
        dialog.grab_set()
        dialog.wait_window()
    
    def show_export_settings(self):
        """Show export settings dialog"""
        dialog = ExportSettingsDialog(self)
        dialog.grab_set()
        dialog.wait_window()
    
    def show_theme_settings(self):
        """Show theme settings dialog"""
        dialog = ThemeSettingsDialog(self)
        dialog.grab_set()
        dialog.wait_window()
    
    def open_output_dir(self):
        """Open the output directory in file explorer"""
        if self.output_dir:
            os.startfile(os.path.realpath(self.output_dir))
    
    def update_recent_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_menu.add_command(
                label=_("No recent files"),
                state="disabled"
            )
            return
        
        for file in self.recent_files:
            self.recent_menu.add_command(
                label=file,
                command=lambda f=file: self.open_recent_file(f)
            )
    
    def add_to_recent_files(self, files):
        """Add files to recent files list"""
        prefs = self.load_preferences()
        recent = prefs.get('recent_files', [])
        
        for file in files:
            if file in recent:
                recent.remove(file)
            recent.insert(0, file)
        
        # Keep only max_recent_files
        recent = recent[:self.max_recent_files]
        
        prefs['recent_files'] = recent
        self.save_preferences(prefs)
        self.recent_files = recent
        self.update_recent_menu()
    
    def open_recent_file(self, file):
        """Open a recent file"""
        if os.path.exists(file):
            self.files_text.delete("1.0", tk.END)
            self.files_text.insert("1.0", file)
        else:
            messagebox.showerror(
                _("Error"),
                _("File not found: {}").format(file)
            )
            # Remove from recent files
            self.recent_files.remove(file)
            prefs = self.load_preferences()
            prefs['recent_files'] = self.recent_files
            self.save_preferences(prefs)
            self.update_recent_menu()

class ExportOptionsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title(_("Export Options"))
        self.geometry("350x350")
        self.configure(bg=COLORS['background'])
        
        # Initialize variables after parent initialization
        self.mobile_var = tk.BooleanVar(master=self, value=False)
        self.print_var = tk.BooleanVar(master=self, value=False)
        self.toc_var = tk.BooleanVar(master=self, value=True)
        
        # Create options frame
        options_frame = ttk.Frame(self, style='Surface.TFrame')
        options_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Add options with dark theme
        checkbutton_style = {'style': 'TCheckbutton'}
        ttk.Checkbutton(
            options_frame,
            text=_("Mobile-friendly layout"),
            variable=self.mobile_var,
            **checkbutton_style
        ).pack(anchor='w', pady=5)
        
        ttk.Checkbutton(
            options_frame,
            text=_("Print-friendly version"),
            variable=self.print_var,
            **checkbutton_style
        ).pack(anchor='w', pady=5)
        
        ttk.Checkbutton(
            options_frame,
            text=_("Include table of contents"),
            variable=self.toc_var,
            **checkbutton_style
        ).pack(anchor='w', pady=5)
        
        # Add options description with dark theme
        desc_text = tk.Text(
            options_frame,
            height=6,
            wrap='word',
            font=('Segoe UI', 9),
            bg=COLORS['surface'],
            fg=COLORS['text_light'],
            insertbackground=COLORS['text']  # Cursor color
        )
        desc_text.pack(fill='both', expand=True, pady=10)
        desc_text.insert('1.0', _("""Mobile-friendly: Optimizes layout for mobile devices
Print-friendly: Adds special styles for printing
Table of contents: Automatically generates navigation
"""))
        desc_text.configure(state='disabled')
        
        # Buttons with dark theme
        button_frame = ttk.Frame(self, style='Surface.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(
            button_frame,
            text=_("Save"),
            command=self.save_and_close,
            style='Primary.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text=_("Cancel"),
            command=self.destroy
        ).pack(side='right')
    
    def save_and_close(self):
        """Save options and close dialog"""
        self.result = {
            'mobile': self.mobile_var.get(),
            'print': self.print_var.get(),
            'toc': self.toc_var.get()
        }
        self.destroy()

class ThemeSettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title(_("Theme Settings"))
        self.geometry("500x400")
        self.configure(bg=COLORS['background'])
        
        # Create main frame with dark theme
        main_frame = ttk.Frame(self, style='Surface.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Theme selector with dark styling
        ttk.Label(
            main_frame,
            text=_("Select Theme:"),
            style='Header.TLabel'
        ).pack(anchor='w', pady=(0, 10))
        
        themes = ['default', 'dark', 'light', 'custom']
        self.theme_var = tk.StringVar(value='dark')  # Set dark as default
        
        for theme in themes:
            rb = ttk.Radiobutton(
                main_frame,
                text=theme.capitalize(),
                value=theme,
                variable=self.theme_var,
                command=self.on_theme_change,
                style='TRadiobutton'
            )
            rb.pack(anchor='w', pady=2)
        
        # Custom colors section
        ttk.Label(
            main_frame,
            text=_("Custom Colors:"),
            style='Header.TLabel'
        ).pack(anchor='w', pady=(20, 10))
        
        color_frame = ttk.Frame(main_frame, style='Surface.TFrame')
        color_frame.pack(fill='x')
        
        self.color_buttons = {}
        colors = {
            'background': _("Background"),
            'text': _("Text"),
            'link': _("Links"),
            'code': _("Code blocks")
        }
        
        for color_key, color_name in colors.items():
            btn = ttk.Button(
                color_frame,
                text=color_name,
                command=lambda k=color_key: self.choose_color(k),
                style='Dropdown.TMenubutton'  # Use dropdown style for better dark theme appearance
            )
            btn.pack(side='left', padx=5)
            self.color_buttons[color_key] = btn
        
        # Preview section with dark theme
        ttk.Label(
            main_frame,
            text=_("Preview:"),
            style='Header.TLabel'
        ).pack(anchor='w', pady=(20, 10))
        
        self.preview = tk.Text(
            main_frame,
            height=8,
            width=40,
            font=('Segoe UI', 10),
            wrap='word',
            bg=COLORS['surface'],
            fg=COLORS['text'],
            insertbackground=COLORS['text']
        )
        self.preview.pack(fill='both', expand=True)
        self.preview.insert('1.0', _("Preview text with some **markdown** and `code`"))
        
        # Buttons with dark theme
        button_frame = ttk.Frame(self, style='Surface.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(
            button_frame,
            text=_("Save"),
            command=self.save_and_close,
            style='Primary.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text=_("Cancel"),
            command=self.destroy,
            style='TButton'
        ).pack(side='right')
        
        # Initialize with dark theme
        self.on_theme_change()
    
    def on_theme_change(self):
        """Handle theme change"""
        theme = self.theme_var.get()
        for btn in self.color_buttons.values():
            btn.configure(state='normal' if theme == 'custom' else 'disabled')
        self.update_preview()
    
    def choose_color(self, color_key):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title=_("Choose color"))
        if color[1]:
            self.color_buttons[color_key].configure(bg=color[1])
            self.update_preview()
    
    def update_preview(self):
        """Update preview text with current theme"""
        theme = self.theme_var.get()
        if theme == 'custom':
            # Apply custom colors
            bg = self.color_buttons['background'].cget('bg')
            fg = self.color_buttons['text'].cget('bg')
            self.preview.configure(bg=bg, fg=fg)
        else:
            # Apply predefined theme
            self.preview.configure(
                bg=COLORS['surface'],
                fg=COLORS['text']
            )
    
    def save_and_close(self):
        """Save theme settings and close dialog"""
        self.result = {
            'theme': self.theme_var.get(),
            'colors': {
                k: btn.cget('bg')
                for k, btn in self.color_buttons.items()
            } if self.theme_var.get() == 'custom' else {}
        }
        self.destroy()

def main():
    if len(sys.argv) > 1:
        app = ReadmeConverter()
        files = sys.argv[1:]
        app.files_text.insert(tk.END, "\n".join(files))
        app.convert_files()
    else:
        app = ReadmeConverter()
        app.mainloop()

if __name__ == '__main__':
    main()
