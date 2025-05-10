import os
import darkdetect
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QSettings

class ThemeManager(QObject):
    """
    Centralized theme manager for the application.
    Handles loading, switching, and applying themes.
    """
    theme_changed = Signal(str)  # Signal emitted when theme changes
    
    def __init__(self, app: QApplication, settings: QSettings):
        super().__init__()
        self.app = app
        self.settings = settings
        self.current_theme = "System Default"
        self.cached_stylesheets = {}
        
    def get_theme(self) -> str:
        """
        Get the current theme setting.
        Returns: "System Default", "Light Theme", or "Dark Theme"
        """
        return self.settings.value("theme", "System Default")
    
    def is_dark_mode(self) -> bool:
        """
        Determine if dark mode is active based on settings and system.
        """
        theme = self.get_theme()
        
        if theme == "System Default":
            return darkdetect.isDark()
        elif theme == "Dark Theme":
            return True
        else:  # Light Theme
            return False
    
    def apply_theme(self):
        """
        Apply the current theme to the application.
        """
        theme = self.get_theme()
        self.current_theme = theme
        
        # Determine which stylesheet to use
        is_dark = self.is_dark_mode()
        stylesheet_path = "resources/styles/dark_style.qss" if is_dark else "resources/styles/light_style.qss"
        
        # Load stylesheet if not cached
        if stylesheet_path not in self.cached_stylesheets:
            try:
                with open(stylesheet_path, "r") as f:
                    self.cached_stylesheets[stylesheet_path] = f.read()
            except Exception as e:
                print(f"Error loading stylesheet: {e}")
                return
        
        # Apply stylesheet
        self.app.setStyleSheet(self.cached_stylesheets[stylesheet_path])
        
        # Emit signal for other components to react
        self.theme_changed.emit(theme)
        
        print(f"Theme applied: {'Dark' if is_dark else 'Light'} Mode") 