import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QGuiApplication, QIcon

from ui.main_window import MainWindow
from ui.theme_manager import ThemeManager

def main():
    # Modern high DPI handling for Qt 6.5+
    # Menghilangkan deprecated attributes dengan pendekatan terbaru
    
    # Set aplikasi untuk high DPI dengan pendekatan modern
    # This must be called before creating the QApplication instance.
    if hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
    app = QApplication(sys.argv)
    
    # AA_EnableHighDpiScaling and AA_UseHighDpiPixmaps are deprecated in Qt6 
    # and high DPI is generally enabled by default.
    # QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    # QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Application configuration
    app.setApplicationName("MetastroDocChecker 2025")
    app.setOrganizationName("MDC-2025")
    app.setApplicationDisplayName("MDC-2025")
    app.setApplicationVersion("1.2.0")
    app.setStyle("Fusion")  # Modern style for consistent look
    
    # Initialize settings
    settings = QSettings("MDC-2025", "Document Checker")
    
    # Initialize theme manager and apply theme
    theme_manager = ThemeManager(app, settings)
    theme_manager.apply_theme()
    
    # Create and show main window - pass theme_manager to constructor
    window = MainWindow()
    window.theme_manager = theme_manager  # Add theme manager to the window
    window.setWindowTitle("MetastroDocChecker 2025 (MDC-2025)")
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 