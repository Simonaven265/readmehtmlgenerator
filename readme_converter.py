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
import json
from datetime import datetime
import gettext

# Set up translation
localedir = Path(__file__).parent / 'locales'
gettext.bindtextdomain('messages', localedir)
gettext.textdomain('messages')
_ = gettext.gettext

class ExportOptionsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("Export Options"))
        self.geometry("300x300")
        self.result = {}
        
        options = ttk.Frame(self)
        options.pack(fill='x', padx=10, pady=5)
        
        # HTML Options
        self.mobile_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text=_("Mobile Optimized"), variable=self.mobile_var).pack(anchor='w', pady=5)
        
        self.print_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text=_("Print Friendly"), variable=self.print_var).pack(anchor='w')
        
        self.toc_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options, text=_("Include Table of Contents"), variable=self.toc_var).pack(anchor='w')
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side='bottom', pady=10)
        ttk.Button(btn_frame, text=_("Export"), command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=_("Cancel"), command=self.cancel).pack(side='left')

    def save(self):
        self.result = {
            'format': 'html',  # Always HTML now
            'mobile': self.mobile_var.get(),
            'print': self.print_var.get(),
            'toc': self.toc_var.get()
        }
        self.destroy()

    def cancel(self):
        self.destroy()

class ExportSettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("Export Settings"))
        self.geometry("500x400")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Filename pattern tab
        filename_frame = ttk.Frame(notebook)
        notebook.add(filename_frame, text=_('Filename'))
        
        ttk.Label(filename_frame, text=_("Filename Pattern:")).pack(anchor='w', pady=5)
        self.pattern_var = tk.StringVar(value="{name}")
        pattern_entry = ttk.Entry(filename_frame, textvariable=self.pattern_var, width=40)
        pattern_entry.pack(fill='x', padx=5)
        
        ttk.Label(filename_frame, text=_("Available patterns:\n{name} - Original filename\n{date} - Current date\n{title} - First heading")).pack(anchor='w', pady=5)
        
        # Metadata tab
        metadata_frame = ttk.Frame(notebook)
        notebook.add(metadata_frame, text=_('Metadata'))
        
        self.metadata = {
            'author': tk.StringVar(),
            'description': tk.StringVar(),
            'keywords': tk.StringVar(),
        }
        
        for key in self.metadata:
            ttk.Label(metadata_frame, text=f"{_(key.title())}:").pack(anchor='w', pady=2)
            ttk.Entry(metadata_frame, textvariable=self.metadata[key], width=40).pack(fill='x', padx=5)
            
        # Header/Footer tab
        custom_frame = ttk.Frame(notebook)
        notebook.add(custom_frame, text=_('Custom HTML'))
        
        ttk.Label(custom_frame, text=_("Custom Header HTML:")).pack(anchor='w', pady=2)
        self.header_text = tk.Text(custom_frame, height=5, width=40)
        self.header_text.pack(fill='x', padx=5)
        
        ttk.Label(custom_frame, text=_("Custom Footer HTML:")).pack(anchor='w', pady=2)
        self.footer_text = tk.Text(custom_frame, height=5, width=40)
        self.footer_text.pack(fill='x', padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=10)
        ttk.Button(btn_frame, text=_("Save"), command=self.save).pack(side='right', padx=5)
        ttk.Button(btn_frame, text=_("Cancel"), command=self.destroy).pack(side='right')

    def save(self):
        self.result = {
            'filename_pattern': self.pattern_var.get(),
            'metadata': {k: v.get() for k, v in self.metadata.items()},
            'header': self.header_text.get('1.0', 'end-1c'),
            'footer': self.footer_text.get('1.0', 'end-1c')
        }
        self.destroy()

class ColorPickerButton(tk.Button):  # Changed from ttk.Button to tk.Button
    def __init__(self, parent, initial_color="#000000", **kwargs):
        super().__init__(parent, **kwargs)
        self.color = initial_color
        self.configure(
            command=self.pick_color,
            width=10,
            background=initial_color,
            relief='solid',
            bd=1
        )

    def pick_color(self):
        # Show color picker dialog
        color = colorchooser.askcolor(self.color, title=_("Choose Color"))[1]
        if color:
            self.color = color
            self.configure(background=color)

    def update_appearance(self):
        self.configure(background=self.color)

class ThemeManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("Theme Manager"))
        self.geometry("800x600")
        self.parent = parent

        # Split into two frames
        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(side='left', fill='y', padx=10, pady=10)

        self.editor_frame = ttk.Frame(self)
        self.editor_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Theme list
        ttk.Label(self.list_frame, text=_("Available Themes:")).pack(anchor='w')
        
        # Theme list with scrollbar
        list_frame = ttk.Frame(self.list_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.theme_list = tk.Listbox(list_frame, width=30, height=20, selectmode='single')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.theme_list.yview)
        self.theme_list.configure(yscrollcommand=scrollbar.set)
        
        self.theme_list.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.theme_list.bind('<<ListboxSelect>>', self.load_theme)

        # Theme list buttons
        btn_frame = ttk.Frame(self.list_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text=_("New Theme"), command=self.new_theme).pack(side='left', padx=2)
        ttk.Button(btn_frame, text=_("Delete"), command=self.delete_theme).pack(side='left', padx=2)

        # Theme editor notebook
        self.notebook = ttk.Notebook(self.editor_frame)
        self.notebook.pack(fill='both', expand=True)

        # General settings tab
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text=_('General'))
        
        # Theme name
        name_frame = ttk.Frame(general_frame)
        name_frame.pack(fill='x', pady=5)
        ttk.Label(name_frame, text=_("Theme Name:")).pack(side='left')
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var).pack(side='left', padx=5, fill='x', expand=True)

        # Color settings
        colors_frame = ttk.LabelFrame(general_frame, text=_("Colors"))
        colors_frame.pack(fill='x', pady=5)

        self.color_pickers = {}
        color_options = {
            'background': _('Background'),
            'text': _('Text Color'),
            'heading': _('Heading Color'),
            'link': _('Link Color'),
            'code_bg': _('Code Background'),
            'code_text': _('Code Text')
        }

        for key, label in color_options.items():
            frame = ttk.Frame(colors_frame)
            frame.pack(fill='x', pady=2)
            ttk.Label(frame, text=label).pack(side='left')
            self.color_pickers[key] = ColorPickerButton(
                frame,
                text="",  # Remove text from button
                initial_color=self.get_default_theme()[key]
            )
            self.color_pickers[key].pack(side='right')

        # Font settings
        font_frame = ttk.LabelFrame(general_frame, text=_("Fonts"))
        font_frame.pack(fill='x', pady=5)

        # Font family
        family_frame = ttk.Frame(font_frame)
        family_frame.pack(fill='x', pady=2)
        ttk.Label(family_frame, text=_("Font Family:")).pack(side='left')
        self.font_family = ttk.Combobox(family_frame, values=[
            "Arial", "Helvetica", "Times New Roman", "Georgia", 
            "Verdana", "Roboto", "Open Sans"
        ])
        self.font_family.pack(side='right', fill='x', expand=True)

        # Font size
        size_frame = ttk.Frame(font_frame)
        size_frame.pack(fill='x', pady=2)
        ttk.Label(size_frame, text=_("Base Font Size:")).pack(side='left')
        self.font_size = ttk.Spinbox(size_frame, from_=8, to=24)
        self.font_size.pack(side='right')

        # Custom CSS and JS tab
        custom_frame = ttk.Frame(self.notebook)
        self.notebook.add(custom_frame, text=_('Custom CSS & JS'))
        
        ttk.Label(custom_frame, text=_("Custom CSS:")).pack(anchor='w', pady=2)
        self.custom_css_text = tk.Text(custom_frame, height=10, width=40)
        self.custom_css_text.pack(fill='x', padx=5)
        
        ttk.Label(custom_frame, text=_("Custom JavaScript:")).pack(anchor='w', pady=2)
        self.custom_js_text = tk.Text(custom_frame, height=10, width=40)
        self.custom_js_text.pack(fill='x', padx=5)

        # Preview tab
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text=_('Preview'))

        # Add file selection frame
        select_frame = ttk.Frame(preview_frame)
        select_frame.pack(fill='x', pady=5)
        
        ttk.Label(select_frame, text=_("Preview file:")).pack(side='left', padx=5)
        self.preview_path = tk.StringVar()
        self.preview_entry = ttk.Entry(select_frame, textvariable=self.preview_path)
        self.preview_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        ttk.Button(select_frame, text=_("Browse"), 
                  command=self.select_preview_file).pack(side='left', padx=5)
        
        # Add preview frame with scrollbar
        preview_content = ttk.Frame(preview_frame)
        preview_content.pack(fill='both', expand=True, pady=5)
        
        self.preview_html = tk.Text(preview_content, wrap='word')
        preview_scroll = ttk.Scrollbar(preview_content, orient='vertical', 
                                     command=self.preview_html.yview)
        self.preview_html.configure(yscrollcommand=preview_scroll.set)
        
        self.preview_html.pack(side='left', fill='both', expand=True)
        preview_scroll.pack(side='right', fill='y')

        # Bottom buttons
        bottom_frame = ttk.Frame(self.editor_frame)
        bottom_frame.pack(fill='x', pady=10)
        ttk.Button(bottom_frame, text=_("Apply"), command=self.apply_theme).pack(side='right', padx=5)
        ttk.Button(bottom_frame, text=_("Save"), command=self.save_theme).pack(side='right', padx=5)

        # Load themes
        self.load_themes()

    def get_preview_content(self):
        return """
        <h1>Theme Preview</h1>
        <p>This is a preview of how your theme will look. It includes various elements:</p>
        
        <h2>Text Formatting</h2>
        <p>Regular text with <strong>bold</strong> and <em>italic</em> formatting.</p>
        <p>Here's a <a href="#">sample link</a> to show link styling.</p>
        
        <h3>Code Examples</h3>
        <p>Inline code: <code>print("Hello World")</code></p>
        <pre><code>def example():
    return "This is a code block"</code></pre>
        
        <h3>Lists</h3>
        <ul>
            <li>List item one</li>
            <li>List item two
                <ul>
                    <li>Nested item</li>
                </ul>
            </li>
        </ul>
        
        <blockquote>
        This is a blockquote to show how quoted text appears.
        </blockquote>
        """

    def new_theme(self):
        name = _("New Theme")
        count = 1
        while name in self.parent.custom_themes:
            name = f"{_('New Theme')} {count}"
            count += 1
            
        self.name_var.set(name)
        self.parent.custom_themes[name] = self.get_default_theme()
        self.load_themes()
        self.theme_list.selection_clear(0, tk.END)
        self.theme_list.selection_set(self.theme_list.get(0, tk.END).index(name))
        self.load_theme()

    def get_default_theme(self):
        return {
            'background': '#ffffff',
            'text': '#333333',
            'heading': '#2c3e50',
            'link': '#3498db',
            'code_bg': '#f5f5f5',
            'code_text': '#333333',
            'font_family': 'Arial',
            'font_size': '16',
            'custom_css': '',
            'custom_js': ''
        }

    def load_themes(self):
        self.theme_list.delete(0, tk.END)
        self.theme_list.insert(tk.END, _("default"))
        
        # Get all themes and sort them
        theme_names = sorted(self.parent.custom_themes.keys())
        
        # Add themes to listbox and mark active theme
        for theme_name in theme_names:
            self.theme_list.insert(tk.END, theme_name)
            # Mark active theme with an asterisk
            if theme_name == self.parent.current_theme:
                idx = self.theme_list.get(0, tk.END).index(theme_name)
                self.theme_list.itemconfig(idx, fg='blue')
                self.theme_list.selection_set(idx)

    def load_theme(self, event=None):
        selection = self.theme_list.curselection()
        if not selection:
            return
            
        theme_name = self.theme_list.get(selection[0])
        self.name_var.set(theme_name)
        
        theme = self.parent.custom_themes.get(theme_name, self.get_default_theme())
        
        for key, picker in self.color_pickers.items():
            picker.color = theme.get(key, '#000000')
            picker.update_appearance()
            
        self.font_family.set(theme.get('font_family', 'Arial'))
        self.font_size.set(theme.get('font_size', '16'))
        self.custom_css_text.delete('1.0', tk.END)
        self.custom_css_text.insert('1.0', theme.get('custom_css', ''))
        self.custom_js_text.delete('1.0', tk.END)
        self.custom_js_text.insert('1.0', theme.get('custom_js', ''))
        self.update_preview()  # Update preview when theme is loaded

    def save_theme(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(_("Error"), _("Theme name cannot be empty"))
            return

        theme = {
            'background': self.color_pickers['background'].color,
            'text': self.color_pickers['text'].color,
            'heading': self.color_pickers['heading'].color,
            'link': self.color_pickers['link'].color,
            'code_bg': self.color_pickers['code_bg'].color,
            'code_text': self.color_pickers['code_text'].color,
            'font_family': self.font_family.get(),
            'font_size': self.font_size.get(),
            'custom_css': self.custom_css_text.get('1.0', 'end-1c'),
            'custom_js': self.custom_js_text.get('1.0', 'end-1c')
        }
        
        self.parent.custom_themes[name] = theme
        self.parent.save_preferences()
        self.load_themes()  # Refresh list to show new theme
        messagebox.showinfo(_("Success"), _("Theme '{name}' saved successfully").format(name=name))
        self.update_preview()  # Update preview when theme is saved

    def apply_theme(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(_("Error"), _("Theme name cannot be empty"))
            return
            
        # Save current theme first
        self.save_theme()
        
        # Update current theme
        self.parent.current_theme = name
        self.parent.save_preferences()
        
        # Refresh theme list to update marking
        self.load_themes()
        
        # Update preview with applied theme
        self.update_preview()
        
        messagebox.showinfo(_("Success"), _("Theme '{name}' applied").format(name=name))

    def delete_theme(self):
        selection = self.theme_list.curselection()
        if not selection:
            return
            
        theme_name = self.theme_list.get(selection[0])
        if theme_name == _("default"):
            messagebox.showerror(_("Error"), _("Cannot delete default theme"))
            return
            
        if messagebox.askyesno(_("Confirm Delete"), _("Delete theme '{theme_name}'?").format(theme_name=theme_name)):
            del self.parent.custom_themes[theme_name]
            self.parent.save_preferences()
            self.load_themes()

    def update_preview(self):
        """Update both code view and preview"""
        # Get current theme settings
        current_theme = {
            'background': self.color_pickers['background'].color,
            'text': self.color_pickers['text'].color,
            'heading': self.color_pickers['heading'].color,
            'link': self.color_pickers['link'].color,
            'code_bg': self.color_pickers['code_bg'].color,
            'code_text': self.color_pickers['code_text'].color,
            'font_family': self.font_family.get(),
            'font_size': self.font_size.get(),
            'custom_css': self.custom_css_text.get('1.0', 'end-1c'),
            'custom_js': self.custom_js_text.get('1.0', 'end-1c')
        }
        
        # Update CSS code view
        css_code = f"""/* Theme: {self.name_var.get()} */
:root {{
    --bg-color: {current_theme['background']};
    --text-color: {current_theme['text']};
    --heading-color: {current_theme['heading']};
    --link-color: {current_theme['link']};
    --code-bg: {current_theme['code_bg']};
    --code-text: {current_theme['code_text']};
}}

body {{
    font-family: {current_theme['font_family']}, sans-serif;
    font-size: {current_theme['font_size']}px;
    background-color: var(--bg-color);
    color: var(--text-color);
}}

h1, h2, h3, h4, h5, h6 {{ color: var(--heading-color); }}
a {{ color: var(--link-color); }}
code, pre {{ 
    background-color: var(--code-bg);
    color: var(--code-text);
}}"""

        # Create preview from selected file or default content
        preview_file = self.preview_path.get()
        if preview_file and os.path.exists(preview_file):
            try:
                with open(preview_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {str(e)}"
        else:
            content = """# Select a file to preview
Click the Browse button above to select a Markdown file for preview."""

        # Convert markdown to HTML
        try:
            html = markdown.markdown(content, extensions=[
                'fenced_code', 'tables', 'codehilite', 'md_in_html'
            ])
        except Exception as e:
            html = f"<p>Error converting markdown: {str(e)}</p>"
        
        # Get CSS
        base_css = read_css()
        
        # Create preview HTML
        preview_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Theme Preview</title>
            <style>
            {base_css}
            {css_code}
            {current_theme['custom_css']}
            </style>
            <script>
            {current_theme['custom_js']}
            </script>
        </head>
        <body>
            <div class="container">
                {html}
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="document.body.classList.toggle('dark-theme')">
                    Toggle Dark Mode
                </button>
            </div>
        </body>
        </html>
        """
        
        # Update preview
        self.preview_html.configure(state='normal')
        self.preview_html.delete('1.0', tk.END)
        self.preview_html.insert('1.0', preview_html)
        self.preview_html.configure(state='disabled')

    def pick_color(self):
        # Show color picker dialog
        color = colorchooser.askcolor(self.color, title=_("Choose Color"))[1]
        if color:
            self.color = color
            self.configure(background=color)
            self.update_preview()  # Update preview when color changes

    def select_preview_file(self):
        """Select a file to preview"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            self.preview_path.set(file_path)
            self.update_preview()

class ExportCustomizationDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("Export Customization"))
        self.geometry("500x600")
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # CSS Injection tab
        css_frame = ttk.Frame(notebook)
        notebook.add(css_frame, text=_('Custom CSS'))
        
        ttk.Label(css_frame, text=_("Additional CSS:")).pack(anchor='w')
        self.css_text = tk.Text(css_frame, height=10)
        self.css_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # JavaScript Injection tab
        js_frame = ttk.Frame(notebook)
        notebook.add(js_frame, text=_('Custom JavaScript'))
        
        ttk.Label(js_frame, text=_("Additional JavaScript:")).pack(anchor='w')
        self.js_text = tk.Text(js_frame, height=10)
        self.js_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Asset Management tab
        asset_frame = ttk.Frame(notebook)
        notebook.add(asset_frame, text=_('Assets'))
        
        self.bundle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(asset_frame, text=_("Bundle assets with HTML"), 
                       variable=self.bundle_var).pack(anchor='w')
        
        self.optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(asset_frame, text=_("Optimize assets"), 
                       variable=self.optimize_var).pack(anchor='w')
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=10)
        ttk.Button(btn_frame, text=_("Save"), command=self.save).pack(side='right', padx=5)
        ttk.Button(btn_frame, text=_("Cancel"), command=self.destroy).pack(side='right')

    def save(self):
        self.result = {
            'custom_css': self.css_text.get('1.0', 'end-1c'),
            'custom_js': self.js_text.get('1.0', 'end-1c'),
            'bundle_assets': self.bundle_var.get(),
            'optimize_assets': self.optimize_var.get()
        }
        self.destroy()

class ReadmeConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title(_("README to HTML Converter"))
        self.geometry("600x400")
        self.output_dir = None
        self.temp_preview_file = None
        self.cancel_conversion = False
        self.recent_files = self.load_preferences().get('recent_files', [])
        self.max_recent_files = 5
        self.export_options = {
            'format': 'html',  # Always HTML now
            'mobile': False,
            'print': False,
            'toc': True
        }
        self.export_settings = {
            'filename_pattern': "{name}",
            'metadata': {},
            'header': "",
            'footer': ""
        }
        self.current_theme = self.load_preferences().get('current_theme', 'default')
        self.custom_themes = self.load_preferences().get('custom_themes', {})
        self.export_customization = {
            'custom_css': '',
            'custom_js': '',
            'bundle_assets': True,
            'optimize_assets': True
        }
        self.create_widgets()
        self.create_menu()

    def create_widgets(self):
        # Create and pack widgets
        self.drop_label = tk.Label(self, text=_("Drop README files here or use the select button"),
                                 bg='#f0f0f0', pady=20)
        self.drop_label.pack(fill=tk.X, pady=10)

        # Configure text widget for drag and drop
        self.files_text = tk.Text(self, height=10, width=60, bg='white')
        self.files_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Enable drag and drop for text widget
        self.files_text.drop_target_register(DND_FILES)
        self.files_text.dnd_bind('<<Drop>>', self.drop_files)

        # Buttons frame
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.select_btn = tk.Button(btn_frame, text=_("Select Files"), command=self.select_files)
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.output_btn = tk.Button(btn_frame, text=_("Select Output Directory"), command=self.select_output_dir)
        self.output_btn.pack(side=tk.LEFT, padx=5)

        self.preview_btn = tk.Button(btn_frame, text=_("Preview"), command=self.preview_files)
        self.preview_btn.pack(side=tk.LEFT, padx=5)

        self.convert_btn = tk.Button(btn_frame, text=_("Convert to HTML"), command=self.convert_files)
        self.convert_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(btn_frame, text=_("Clear"), command=self.clear_files)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        # Add progress bar and cancel button
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_bar = Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.cancel_btn = tk.Button(self.progress_frame, text=_("Cancel"), command=self.cancel_conversion_task)
        self.cancel_btn.pack(side=tk.RIGHT)
        self.cancel_btn.pack_forget()  # Hide initially

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("File"), menu=file_menu)
        file_menu.add_command(label=_("Select Files"), command=self.select_files)
        file_menu.add_command(label=_("Select Output Directory"), command=self.select_output_dir)
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label=_("Recent Files"), menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label=_("Clear Recent Files"), command=self.clear_recent_files)
        file_menu.add_separator()
        file_menu.add_command(label=_("Exit"), command=self.quit)

        # Export menu
        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Export"), menu=export_menu)
        export_menu.add_command(label=_("Export Options..."), command=self.show_export_options)
        export_menu.add_command(label=_("Export Settings..."), command=self.show_export_settings)
        export_menu.add_separator()
        export_menu.add_command(label=_("Quick Export"), command=lambda: self.convert_files(quick=True))
        export_menu.add_command(label=_("Customize Export..."), command=self.show_export_customization)

        # Add Themes menu
        themes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Themes"), menu=themes_menu)
        themes_menu.add_command(label=_("Theme Manager..."), command=self.show_theme_manager)

    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        for path in self.recent_files:
            self.recent_menu.add_command(
                label=path,
                command=lambda p=path: self.load_recent_file(p)
            )

    def load_recent_file(self, path):
        if os.path.exists(path):
            self.files_text.delete(1.0, tk.END)
            self.files_text.insert(tk.END, path)
        else:
            messagebox.showerror(_("Error"), _("File not found: {path}").format(path=path))
            self.recent_files.remove(path)
            self.save_preferences()
            self.update_recent_menu()

    def clear_recent_files(self):
        self.recent_files = []
        self.save_preferences()
        self.update_recent_menu()

    def add_to_recent_files(self, files):
        for file in files:
            if file in self.recent_files:
                self.recent_files.remove(file)
            self.recent_files.insert(0, file)
        
        # Keep only max_recent_files
        self.recent_files = self.recent_files[:self.max_recent_files]
        self.save_preferences()
        self.update_recent_menu()

    def load_preferences(self):
        try:
            with open(Path(__file__).parent / 'preferences.json', 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_preferences(self):
        prefs = {
            'recent_files': self.recent_files,
            'output_dir': self.output_dir,
            'export_settings': self.export_settings,  # Add export settings to preferences
            'current_theme': self.current_theme,
            'custom_themes': self.custom_themes,
            'export_customization': self.export_customization
        }
        try:
            with open(Path(__file__).parent / 'preferences.json', 'w') as f:
                json.dump(prefs, f)
        except Exception as e:
            print(f"Failed to save preferences: {e}")

    def drop_files(self, event):
        # Get the dropped files
        files = self.files_text.tk.splitlist(event.data)
        # Filter only .md files
        md_files = [f for f in files if f.lower().endswith('.md')]
        
        # Add to existing files
        current_files = self.files_text.get(1.0, tk.END).strip().split('\n')
        current_files = [f for f in current_files if f]  # Remove empty strings
        
        # Combine and remove duplicates while preserving order
        all_files = []
        seen = set()
        for f in current_files + md_files:
            if f not in seen:
                all_files.append(f)
                seen.add(f)

        # Update text widget
        self.files_text.delete(1.0, tk.END)
        self.files_text.insert(tk.END, '\n'.join(all_files))
        
        # Update drop label
        self.drop_label.configure(text=f"{len(all_files)} files selected")

    def clear_files(self):
        self.files_text.delete(1.0, tk.END)
        self.drop_label.configure(text=_("Drop README files here or use the select button"))
        self.progress_bar['value'] = 0
        self.cancel_btn.pack_forget()

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if files:
            self.files_text.delete(1.0, tk.END)
            self.files_text.insert(tk.END, "\n".join(files))
            self.add_to_recent_files(files)

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            messagebox.showinfo(_("Output Directory"), _("Selected output directory: {self.output_dir}").format(self=self))
            self.save_preferences()

    def preview_files(self):
        files = self.files_text.get(1.0, tk.END).strip().split("\n")
        if not files or not files[0]:
            messagebox.showwarning(_("Warning"), _("Please select files to preview"))
            return

        try:
            # Create preview for the first file
            preview_html = self.convert_readme_to_html(files[0], preview_mode=True)
            
            # Create temporary file for preview
            if self.temp_preview_file:
                try:
                    os.unlink(self.temp_preview_file)
                except:
                    pass
            
            # Create temporary file in system temp directory
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
                f.write(preview_html)
                self.temp_preview_file = f.name

            # Open in default browser
            webbrowser.open(f'file://{self.temp_preview_file}')

        except Exception as e:
            messagebox.showerror(_("Preview Error"), str(e))

    def convert_files(self, quick=False, format=None):
        files = self.files_text.get(1.0, tk.END).strip().split("\n")
        files = [f for f in files if f]
        
        if not files:
            messagebox.showwarning(_("Warning"), _("No files selected"))
            return
            
        # Reset cancel flag
        self.cancel_conversion = False
        
        # Show cancel button and reset progress
        self.cancel_btn.pack(side=tk.RIGHT)
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(files)
        
        # Start conversion in separate thread
        conversion_thread = threading.Thread(target=self._convert_files_thread, args=(files,))
        conversion_thread.start()

    def _convert_files_thread(self, files):
        successful = 0
        failed = 0
        
        for i, file in enumerate(files):
            if self.cancel_conversion:
                break
                
            try:
                output_path = self.convert_readme_to_html(file, self.output_dir)
                successful += 1
                # Update UI from main thread
                self.after(0, self._update_progress, i + 1, _("Converted {file} to {output_path}").format(file=file, output_path=output_path))
            except Exception as e:
                failed += 1
                self.after(0, self._show_error, _("Failed to convert {file}: {e}").format(file=file, e=e))

            if self.cancel_conversion:
                break

        # Final update
        self.after(0, self._finish_conversion, successful, failed)

    def _update_progress(self, value, message):
        self.progress_bar['value'] = value
        self.drop_label.configure(text=message)

    def _show_error(self, message):
        messagebox.showerror(_("Error"), message)

    def _finish_conversion(self, successful, failed):
        self.cancel_btn.pack_forget()
        total = successful + failed
        status = _("Completed: {successful} successful, {failed} failed").format(successful=successful, failed=failed)
        if self.cancel_conversion:
            status = _("Conversion cancelled. ") + status
        messagebox.showinfo(_("Conversion Complete"), status)
        self.drop_label.configure(text=_("Drop README files here or use the select button"))

    def cancel_conversion_task(self):
        self.cancel_conversion = True

    def show_export_options(self):
        dialog = ExportOptionsDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.export_options.update(dialog.result)
            self.convert_files()

    def show_export_settings(self):
        dialog = ExportSettingsDialog(self)
        self.wait_window(dialog)
        if hasattr(dialog, 'result'):
            self.export_settings.update(dialog.result)

    def show_theme_manager(self):
        dialog = ThemeManagerDialog(self)
        self.wait_window(dialog)
        if hasattr(dialog, 'result'):
            self.current_theme = dialog.result
            self.save_preferences()

    def show_export_customization(self):
        dialog = ExportCustomizationDialog(self)
        self.wait_window(dialog)
        if hasattr(dialog, 'result'):
            self.export_customization.update(dialog.result)
            self.save_preferences()

    def __del__(self):
        # Cleanup temporary files
        if self.temp_preview_file and os.path.exists(self.temp_preview_file):
            try:
                os.unlink(self.temp_preview_file)
            except:
                pass

    def get_theme_css(self):
        """Generate CSS from current theme"""
        theme = self.custom_themes.get(self.current_theme, {})
        if not theme:
            return ""

        return f"""
        body {{
            background-color: {theme.get('background', '#ffffff')};
            color: {theme.get('text', '#333333')};
            font-family: {theme.get('font_family', 'Arial')}, sans-serif;
            font-size: {theme.get('font_size', '16')}px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {theme.get('heading', '#2c3e50')};
        }}

        a {{
            color: {theme.get('link', '#3498db')};
        }}

        code, pre {{
            background-color: {theme.get('code_bg', '#f5f5f5')};
            color: {theme.get('code_text', '#333333')};
        }}

        .dark-theme {{
            background-color: {theme.get('background', '#1a1a1a')};
            color: {theme.get('text', '#e0e0e0')};
        }}

        .dark-theme h1,
        .dark-theme h2,
        .dark-theme h3,
        .dark-theme h4,
        .dark-theme h5,
        .dark-theme h6 {{
            color: {theme.get('heading', '#81a1c1')};
        }}

        .dark-theme a {{
            color: {theme.get('link', '#88c0d0')};
        }}

        .dark-theme code,
        .dark-theme pre {{
            background-color: {theme.get('code_bg', '#3b3b3b')};
            color: {theme.get('code_text', '#e0e0e0')};
        }}
        """

    def convert_readme_to_html(self, readme_path, output_dir=None, preview_mode=False):
        # Read README file
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert markdown to HTML with syntax highlighting
        html = markdown.markdown(content, extensions=[
            'fenced_code',
            'tables',
            'codehilite',
            'md_in_html'
        ])
        
        # Embed images
        html = self.embed_images(html, readme_path)
        
        # Get base CSS and theme CSS
        base_css = read_css()
        theme_css = self.get_theme_css()
        
        # Generate TOC if enabled
        toc_html = ""
        if self.export_options['toc'] and not preview_mode:
            toc_html = self.generate_toc(html)

        # Add mobile meta tag if needed
        mobile_meta = """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        """ if self.export_options['mobile'] else ""

        # Add print styles if needed
        print_styles = """
        @media print {
            .theme-toggle { display: none; }
            .container { box-shadow: none; }
            a { text-decoration: underline; }
        }
        """ if self.export_options['print'] else ""

        # Get first heading for title
        first_heading = None
        for line in content.splitlines():
            if line.startswith('# '):
                first_heading = line[2:].strip()
                break
        title = first_heading if first_heading else Path(readme_path).stem
        
        # Generate filename from pattern
        filename = self.export_settings['filename_pattern'].format(
            name=Path(readme_path).stem,
            date=datetime.now().strftime('%Y-%m-%d'),
            title=title.replace(' ', '-')
        )
        
        # Add metadata
        metadata = '\n'.join([
            f'<meta name="{key}" content="{value}">'
            for key, value in self.export_settings['metadata'].items()
            if value
        ])
        
        # Add custom CSS and JavaScript
        custom_css = f"\n/* Custom CSS */\n{self.export_customization['custom_css']}" if self.export_customization['custom_css'] else ""
        custom_js = f"\n/* Custom JavaScript */\n{self.export_customization['custom_js']}" if self.export_customization['custom_js'] else ""
        
        # Create full HTML document
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {mobile_meta}
            {metadata}
            <style>
            {base_css}
            {theme_css}
            {print_styles}
            {custom_css}
            </style>
            <script>
            {custom_js}
            function toggleTheme() {{
                document.body.classList.toggle('dark-theme');
                localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
            }}
            
            // Check saved theme preference
            if (localStorage.getItem('theme') === 'dark') {{
                document.body.classList.add('dark-theme');
            }}
            </script>
        </head>
        <body>
            <div class="theme-toggle">
                <button onclick="toggleTheme()">Toggle Theme</button>
            </div>
            {self.export_settings['header']}
            {toc_html}
            <div class="container">
                {html}
            </div>
            {self.export_settings['footer']}
        </body>
        </html>
        """
        
        if preview_mode:
            return html_template
        
        # Generate output path with custom filename
        output_path = Path(readme_path).with_suffix('').with_name(filename + '.html')
        if output_dir:
            output_path = Path(output_dir) / output_path.name

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)

        return output_path

    def embed_images(self, html, base_path):
        """Embed images as base64 in the HTML content."""
        def replace_image(match):
            img_tag = match.group(0)
            img_src = match.group(1)
            img_path = urljoin(f'file://{base_path}', img_src)
            try:
                with open(img_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    img_ext = os.path.splitext(img_path)[1][1:]
                    return img_tag.replace(img_src, f'data:image/{img_ext};base64,{img_base64}')
            except Exception as e:
                print(f"Failed to embed image {img_src}: {e}")
                return img_tag

        return html.replace('<img src="', '<img src="data:image/')

    def generate_toc(self, html):
        """Generate table of contents from HTML content"""
        headers = []
        for line in html.splitlines():
            if line.startswith('<h') and line[2].isdigit() and line[3] == '>':
                level = int(line[2])
                title = line[4:line.index('</h')].strip()
                headers.append((level, title))
        
        if not headers:
            return ""
        
        toc = ['<div class="toc"><h2>Table of Contents</h2><ul>']
        for level, title in headers:
            anchor = title.lower().replace(' ', '-')
            toc.append(f'<li class="toc-h{level}"><a href="#{anchor}">{title}</a></li>')
            html = html.replace(f'<h{level}>{title}</h{level}>', f'<h{level} id="{anchor}">{title}</h{level}>')
        
        toc.append('</ul></div>')
        return '\n'.join(toc)

def read_css():
    css_path = Path(__file__).parent / 'styles.css'
    with open(css_path, 'r') as f:
        return f.read()

def main():
    if len(sys.argv) > 1:
        # Command line mode
        readme_path = sys.argv[1]
        if not os.path.exists(readme_path):
            print(f"Error: File {readme_path} not found")
            return
        output_path = convert_readme_to_html(readme_path)
        print(f"Successfully converted! Output saved to: {output_path}")
    else:
        # GUI mode
        app = ReadmeConverter()
        app.mainloop()

if __name__ == "__main__":
    main()
