# README HTML Generator

A modern GUI application for converting Markdown README files to beautifully styled HTML documents.

## Features

- 🎨 Modern, clean interface with dark/light theme support
- 📱 Responsive output with mobile-friendly options
- 🖨️ Print-friendly version generation
- 📑 Automatic table of contents generation
- 🎭 Custom theme editor with live preview
- 📋 Drag and drop file support
- 🔄 Recent files management
- 🌍 Internationalization support
- ⚡ Background processing for large files
- 📝 Markdown syntax highlighting
- 🖼️ Image embedding support
- 🎯 Code syntax highlighting

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python readme_converter.py
   ```

2. Add README files by either:
   - Dragging and dropping files into the application window
   - Clicking "Browse Files" to select files
   - Using recent files from the File menu

3. Click "Convert to HTML" to process the files

4. Select an output directory for the converted files

## Configuration

### Export Options

- Mobile-friendly layout: Optimizes the output for mobile devices
- Print-friendly version: Adds print-specific styling
- Table of contents: Automatically generates a navigation menu

### Theme Settings

- Choose from predefined themes (Default, Dark, Light)
- Create custom themes with personalized colors
- Live preview of theme changes

### Export Settings

- Customize output filenames
- Add metadata (author, description, keywords)
- Configure header and footer content

## Command Line Usage

You can also use the application from the command line:

```bash
python readme_converter.py file1.md file2.md
```

This will automatically convert the specified files and prompt for an output directory.

## Development

The application is built using:
- Python 3.7+
- Tkinter for the GUI
- markdown for Markdown processing
- Pygments for syntax highlighting

### Project Structure

```
readmehtmlgenerator/
├── readme_converter.py   # Main application
├── requirements.txt      # Python dependencies
├── styles.css           # Default CSS styles
├── preferences.json     # User preferences
└── README.md           # Documentation
```

## License

This project is MIT licensed. Feel free to use, modify, and distribute as you wish.