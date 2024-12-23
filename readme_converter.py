import markdown
import os
import sys
from pathlib import Path

def read_css():
    css_path = Path(__file__).parent / 'styles.css'
    with open(css_path, 'r') as f:
        return f.read()

def convert_readme_to_html(readme_path):
    # Read README file
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown to HTML
    html = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    
    # Get CSS
    css = read_css()
    
    # Create full HTML document
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
        {css}
        </style>
    </head>
    <body>
        <div class="container">
            {html}
        </div>
    </body>
    </html>
    """
    
    # Generate output path
    output_path = Path(readme_path).with_suffix('.html')
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python readme_converter.py <path_to_readme>")
        return

    readme_path = sys.argv[1]
    if not os.path.exists(readme_path):
        print(f"Error: File {readme_path} not found")
        return

    output_path = convert_readme_to_html(readme_path)
    print(f"Successfully converted! Output saved to: {output_path}")

if __name__ == "__main__":
    main()
