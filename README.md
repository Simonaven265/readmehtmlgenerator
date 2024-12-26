# README to HTML Converter

This project is a GUI application that converts Markdown README files to HTML. It allows users to customize themes, inject custom CSS and JavaScript, and preview the converted HTML.

## Features

- Drag and drop support for Markdown files
- Theme management with color, font, and custom CSS/JS settings
- Live preview of the converted HTML with the selected theme
- Export options for mobile optimization, print-friendly format, and table of contents
- Recent files list for quick access
- Localization support

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/readme-to-html.git
    cd readme-to-html
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```sh
    python readme_converter.py
    ```

2. Drag and drop Markdown files into the application or use the "Select Files" button to choose files.

3. Customize the theme using the "Theme Manager" under the "Themes" menu.

4. Preview the converted HTML by clicking the "Preview" button.

5. Export the HTML using the "Convert to HTML" button or customize export settings under the "Export" menu.

## Theme Management

The Theme Manager allows you to create, edit, and delete themes. You can customize the following settings:

- Background color
- Text color
- Heading color
- Link color
- Code background color
- Code text color
- Font family
- Font size
- Custom CSS
- Custom JavaScript

## Export Options

The Export Options dialog allows you to customize the export settings:

- Mobile Optimized: Adds a viewport meta tag for responsive design.
- Print Friendly: Adds print styles for better print formatting.
- Include Table of Contents: Generates a table of contents based on the headings in the Markdown file.

## Localization

The application supports localization. To add a new language, create a `.po` file in the `locales` directory and compile it to a `.mo` file.

⠀⠀⠀⠀⠀ ⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⠀⣀⡀⠀⠀⠀⠀⠀⠀
⠀⠀⣀⡴⠞⠉⢉⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢯⡉⠙⠳⣦⡀⠀⠀
⢀⣼⠋⠀⠀⢀⣤⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣄⠀⠀⠈⠻⣆⠀
⣼⠃⠀⠀⣰⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄⠀⠀⠹⡇
⡟⠀⠀⢰⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀ ⠀⣿
⣿⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⠀⠀⢠⡿
⠘⣷⡀⠀⠘⢷⣄⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣴⠟⠁⠀⣠⡾⠁
⠀⠈⠻⣦⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⣼⠋⠀⠀
⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⢸⡇⠀⠀⠀
⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⢸⡇⠀⠀
⠀⠀⠀⢸⡇⢠⣶⣿⣿⣦⡀⠀⠀⠀  ⡠⣦⣿⣷⣦⡀⢸⡇⠀⠀⠀
⠀⠀⠀⠸⡇⣿⣿⣿⣿⣿⣶⠀⠀⠀  ⣿⣿⣿⣿⣿⣶⢸⡇⠀⠀⠀
⠀⠀⠀⢰⣇⢻⣿⣿⣿⣿⡟⠀⠀⠀  ⢿⣿⣿⣿⣟⡟⣼⠃⠀⠀⠀
⠀⠀⠀⠀⣻⣆⠙⠛⠛⠋⠀⠀⠀⠀  ⠈⠙ ⠛⠛⢁⣴⠏⠀⠀⠀⠀
⠀⠀⠀⠀⠻⣿⡿⣶⣦⣤⣤⣀⣀⣀⣀⣤⣤⡶⠖⠋⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⢻⡆⣱⣾⠟⠉⣽⢋⡟⣯⠻⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠻⣿⠟⠁⣠⡾⠁⠜⢸⡉⠁⡽⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡏⣠⡾⠋⢀⠆⠀⣼⢷⡀⠸⣽⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⠉⣀⡴⠋⠀⣰⢿⠀⠻⣄⢹⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣸⣡⡾⠋⠀⣠⣷⣿⡈⢧⡀⠘⣾⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⠏⠄⢠⣾⣿⣿⣿⣿⣌⠳⣄⢹⡷⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠹⣧⡷⠏⣿⣿⡏⠈⣿⣿⣿⣾⣿⠛⠻⠷⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠉⠀ ⠀⢹⣿⡇ ⠀⣿⡟⠈⠉⠋⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠉⠀     ⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀