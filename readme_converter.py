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

class ReadmeConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("README to HTML Converter")
        self.geometry("600x400")
        self.output_dir = None
        self.temp_preview_file = None
        self.cancel_conversion = False
        self.recent_files = self.load_preferences().get('recent_files', [])
        self.max_recent_files = 5
        self.create_widgets()
        self.create_menu()

    def create_widgets(self):
        # Create and pack widgets
        self.drop_label = tk.Label(self, text="Drop README files here or use the select button",
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

        self.select_btn = tk.Button(btn_frame, text="Select Files", command=self.select_files)
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.output_btn = tk.Button(btn_frame, text="Select Output Directory", command=self.select_output_dir)
        self.output_btn.pack(side=tk.LEFT, padx=5)

        self.preview_btn = tk.Button(btn_frame, text="Preview", command=self.preview_files)
        self.preview_btn.pack(side=tk.LEFT, padx=5)

        self.convert_btn = tk.Button(btn_frame, text="Convert to HTML", command=self.convert_files)
        self.convert_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_files)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        # Add progress bar and cancel button
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_bar = Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.cancel_btn = tk.Button(self.progress_frame, text="Cancel", command=self.cancel_conversion_task)
        self.cancel_btn.pack(side=tk.RIGHT)
        self.cancel_btn.pack_forget()  # Hide initially

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Files", command=self.select_files)
        file_menu.add_command(label="Select Output Directory", command=self.select_output_dir)
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Clear Recent Files", command=self.clear_recent_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

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
            messagebox.showerror("Error", f"File not found: {path}")
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
            'output_dir': self.output_dir
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
        self.drop_label.configure(text="Drop README files here or use the select button")
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
            messagebox.showinfo("Output Directory", f"Selected output directory: {self.output_dir}")
            self.save_preferences()

    def preview_files(self):
        files = self.files_text.get(1.0, tk.END).strip().split("\n")
        if not files or not files[0]:
            messagebox.showwarning("Warning", "Please select files to preview")
            return

        try:
            # Create preview for the first file
            preview_html = convert_readme_to_html(files[0], preview_mode=True)
            
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
            messagebox.showerror("Preview Error", str(e))

    def convert_files(self):
        files = self.files_text.get(1.0, tk.END).strip().split("\n")
        files = [f for f in files if f]
        
        if not files:
            messagebox.showwarning("Warning", "No files selected")
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
                output_path = convert_readme_to_html(file, self.output_dir)
                successful += 1
                # Update UI from main thread
                self.after(0, self._update_progress, i + 1, f"Converted {file} to {output_path}")
            except Exception as e:
                failed += 1
                self.after(0, self._show_error, f"Failed to convert {file}: {str(e)}")

            if self.cancel_conversion:
                break

        # Final update
        self.after(0, self._finish_conversion, successful, failed)

    def _update_progress(self, value, message):
        self.progress_bar['value'] = value
        self.drop_label.configure(text=message)

    def _show_error(self, message):
        messagebox.showerror("Error", message)

    def _finish_conversion(self, successful, failed):
        self.cancel_btn.pack_forget()
        total = successful + failed
        status = f"Completed: {successful} successful, {failed} failed"
        if self.cancel_conversion:
            status = "Conversion cancelled. " + status
        messagebox.showinfo("Conversion Complete", status)
        self.drop_label.configure(text="Drop README files here or use the select button")

    def cancel_conversion_task(self):
        self.cancel_conversion = True

    def __del__(self):
        # Cleanup temporary files
        if self.temp_preview_file and os.path.exists(self.temp_preview_file):
            try:
                os.unlink(self.temp_preview_file)
            except:
                pass

def read_css():
    css_path = Path(__file__).parent / 'styles.css'
    with open(css_path, 'r') as f:
        return f.read()

def convert_readme_to_html(readme_path, output_dir=None, preview_mode=False):
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
    
    # Get CSS
    css = read_css()
    
    # Create full HTML document with theme toggle
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
        {css}
        </style>
        <script>
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
        <div class="container">
            {html}
        </div>
    </body>
    </html>
    """
    
    if preview_mode:
        return html_template
    
    # Generate output path
    output_path = Path(readme_path).with_suffix('.html')
    if output_dir:
        output_path = Path(output_dir) / output_path.name
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

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
