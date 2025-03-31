# README HTML Generator

A program for converting Markdown files to HTML with advanced customization options. The application enables creating elegant HTML documents from README files and other Markdown documents with the ability to personalize appearance, add custom CSS, and JavaScript.

## Main Features

- **Easy Markdown to HTML Conversion**:
  - Drag and drop Markdown files into the application
  - Support for Markdown syntax with extensions (code blocks, tables, syntax highlighting)
  - Preview conversion before saving

- **Advanced Theme Management**:
  - Create, edit, and delete custom themes
  - Full control over colors (background, text, headings, links, code blocks)
  - Choose font family and text size
  - Real-time theme preview
  - Switch between light and dark modes

- **Flexible Export Options**:
  - Mobile optimization
  - Print-friendly mode
  - Automatic table of contents generation
  - Embedded images in HTML file
  - Add custom metadata

- **Advanced Customization**:
  - Inject custom CSS and JavaScript code
  - Add custom HTML headers and footers
  - Asset handling options (bundling, optimization)
  - Custom output filename patterns

- **User-Friendly Interface**:
  - Modern design with blue-turquoise color scheme
  - Recently used files list
  - Multi-language support (localization)
  - Progress bar with conversion cancellation option

## System Requirements

- Python 3.6 or newer
- Dependencies:
  - markdown
  - tkinterdnd2
  - webbrowser
  - PIL (optional, for image handling)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/simonaven265/readmehtmlgenerator.git
   cd readmehtmlgenerator
   ```

2. Install required packages:
   ```sh
   pip install -r requirements.txt
   ```

## How to Use

1. Run the application:
   ```sh
   python readme_converter.py
   ```

2. Drag Markdown files into the application window or use the "Select Files" button

3. Choose output directory by clicking "Output Directory" (optional)

4. Customize export options from the "Export" → "Export Options..." menu

5. You can preview the result by clicking the "Preview" button

6. Click "Convert to HTML" to convert files

## Theme Management

In the Theme Manager (accessible via the 🎨 button) you can:

- Create new themes
- Edit existing themes
- Customize:
  - Background, text, heading, and link colors
  - Code block colors and styles
  - Fonts and text sizes
  - Add custom CSS and JavaScript
- See a preview of the theme on a selected Markdown file
- Apply a theme as default

## Export Options

In the "Export Options" window you can adjust:

- **Mobile Format**: optimizes HTML for mobile devices
- **Print Format**: adds styles to facilitate printing
- **Table of Contents**: automatically generates a table of contents based on headings

In the "Export Settings" window you can set:

- **Filename Pattern**: customize the output filename
- **Metadata**: add author, description, keywords
- **Custom HTML**: add custom header and footer

## Advanced Customization

In the "Export Customization" tab (⚙️ button) you can:

- Add custom CSS code
- Add custom JavaScript code
- Enable asset bundling with HTML
- Enable asset optimization

## Multi-language Support

The application supports interface translation. To add a new language:

1. Create a `.po` file in the `locales` directory
2. Compile it to a `.mo` file
3. The language will be automatically detected based on system settings

## Tips

- You can quickly export files using "Quick Export" from the Export menu
- Use table of contents for long documents to facilitate navigation
- All settings are automatically saved in the preferences.json file
- Switching between light/dark mode is available in the exported HTML

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
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠉⠀     ⠉