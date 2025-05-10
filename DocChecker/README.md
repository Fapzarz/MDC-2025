# MetastroDocChecker 2025 (MDC-2025)

A modern Windows desktop application for checking document formatting compliance.

## Features

- **Modern UI/UX**: Clean, intuitive interface with both light and dark themes
- **Format Rules Checking**: Verify documents against predefined formatting rules
  - Font type (Times New Roman)
  - Font size (12pt)
  - Line spacing (1.5)
  - Margins (4cm left, 3cm right/top/bottom)
- **Batch Processing**: Check multiple documents simultaneously with multi-threading
- **Detailed Reports**: View comprehensive formatting issue reports with summary and details view
- **Customizable Settings**: Adjust rules and preferences as needed
- **Support for Multiple Formats**: Works with both DOCX and PDF files
- **Enhanced Performance**: Multi-threaded batch processing for faster document validation

## Requirements

- Windows 10 or later
- Python 3.8 or later
- Required Python packages (see requirements.txt)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Run the application:

```
python src/main.py
```

Alternatively, use the included `run.bat` file for easy startup.

## How to Use

1. **Add Documents**: 
   - Drag and drop files into the application
   - Or click "Add Files" to select documents through a file dialog

2. **Check Documents**:
   - Click on a file in the list to check it individually
   - Or click "Check All Files" to process all added documents at once

3. **View Results**:
   - Summary tab shows overall status and issues
   - Details tab shows specific formatting problems
   - For batch processing, the Files tab lists all processed documents

4. **Customize Settings**:
   - Click the ⚙️ Settings button to adjust preferences
   - Modify document rules in the Document Rules tab
   - Change interface options and export preferences

## Customization

The application allows customization of:

- Document formatting rules (font, size, margins, spacing)
- Interface theme (Light/Dark/System)
- Report export settings
- Default save locations

## Technical Details

- Built using PySide6 (Qt for Python) for modern UI
- Multi-threaded document processing with QThreadPool
- Document parsing with python-docx and PyMuPDF
- Modern high DPI support with Qt 6
- Dark mode detection and automatic theme switching

## License

This project is available under the MIT License.

## Acknowledgements

- Built using PySide6 (Qt for Python)
- Document parsing powered by python-docx and PyMuPDF
- User interface designed for maximum usability and efficiency 