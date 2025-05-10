# MetastroDocChecker 2025

A modern document validation application for ensuring compliance with formatting standards.

## About

MetastroDocChecker 2025 is designed to validate DOCX and PDF documents against predefined formatting standards. It features a modern UI with theme support, batch processing capabilities, and detailed report generation.

## Running the Application

### Requirements
- Python 3.8 or newer
- PySide6
- Other dependencies listed in `requirements.txt`

### Installation
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python src/main.py
   ```
   
   Alternatively, on Windows, you can use:
   ```
   run.bat
   ```

## Features

- **Document Validation**: Check documents against predefined formatting rules
- **Theme Support**: Light, Dark, and System themes available
- **Batch Processing**: Process multiple documents at once
- **Detailed Reports**: Get comprehensive reports on formatting issues

## Project Structure

```
DocChecker/
├── resources/              # Application resources
│   ├── icons/              # Icons used in the application
│   ├── screenshots/        # Application screenshots
│   ├── styles/             # QSS stylesheets
│   └── qss/                # Resource files
├── src/                    # Source code
│   ├── core/               # Core functionality
│   │   ├── document_checker.py    # Document validation logic
│   │   └── logger_config.py       # Logging configuration
│   ├── ui/                 # User interface components
│   │   ├── main_window.py         # Main application window
│   │   ├── theme_manager.py       # Theme management
│   │   └── widgets/              # UI widgets
│   └── main.py             # Application entry point
├── requirements.txt        # Python dependencies
├── run.bat                 # Windows batch file to run the application
└── README.md               # This file
```

## Development

To contribute to this project, please see the main [CONTRIBUTING.md](../CONTRIBUTING.md) file in the parent directory.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file in the parent directory for details. 