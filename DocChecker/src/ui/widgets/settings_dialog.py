from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QCheckBox,
    QPushButton, QTabWidget, QWidget, QGroupBox,
    QComboBox, QColorDialog, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSettings

class SettingsDialog(QDialog):
    settings_changed = Signal()
    
    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Pengaturan Document Checker")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Gunakan instance QSettings yang diberikan
        self.settings = settings
        self.parent_window = parent
        
        # Setup layout
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.general_tab = self._create_general_tab()
        self.rules_tab = self._create_rules_tab()
        self.export_tab = self._create_export_tab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.rules_tab, "Document Rules")
        self.tab_widget.addTab(self.export_tab, "Export")
        
        # Add tab widget to main layout
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self._save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_settings)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Load current values
        self._load_settings()
        
        # Connect theme combo box change signal for live preview
        self.theme_combo.currentTextChanged.connect(self._handle_theme_preview)
        
    def _create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Interface group
        interface_group = QGroupBox("Interface")
        interface_layout = QFormLayout(interface_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System Default", "Light Theme", "Dark Theme"])
        interface_layout.addRow("Theme:", self.theme_combo)
        
        self.apply_theme_check = QCheckBox("Preview theme changes immediately")
        self.apply_theme_check.setChecked(True)
        interface_layout.addRow("", self.apply_theme_check)
        
        self.show_icons_check = QCheckBox("Show file type icons")
        interface_layout.addRow("", self.show_icons_check)
        
        # Batch processing group
        batch_group = QGroupBox("Pemrosesan Batch")
        batch_layout = QFormLayout(batch_group)
        
        self.auto_save_reports_check = QCheckBox("Simpan laporan otomatis setelah pemrosesan batch")
        batch_layout.addRow("", self.auto_save_reports_check)
        
        self.report_folder_edit = QLineEdit()
        self.report_folder_button = QPushButton("Jelajahi...")
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.report_folder_edit)
        folder_layout.addWidget(self.report_folder_button)
        batch_layout.addRow("Folder laporan:", folder_layout)
        
        self.report_folder_button.clicked.connect(self._select_report_folder)
        
        # Developer group
        developer_group = QGroupBox("Developer")
        developer_layout = QFormLayout(developer_group)
        
        self.extensive_logging_check = QCheckBox("Aktifkan logging ekstensif")
        developer_layout.addRow("Logging:", self.extensive_logging_check)
        
        # Add groups to layout
        layout.addWidget(interface_group)
        layout.addWidget(batch_group)
        layout.addWidget(developer_group)
        layout.addStretch()
        
        return tab
        
    def _create_rules_tab(self):
        """Create document rules tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Font rules group
        font_group = QGroupBox("Font Rules")
        font_layout = QFormLayout(font_group)
        
        self.font_name_edit = QLineEdit()
        font_layout.addRow("Required Font:", self.font_name_edit)
        
        self.font_size_spin = QDoubleSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setSingleStep(0.5)
        self.font_size_spin.setDecimals(1)
        font_layout.addRow("Font Size (pt):", self.font_size_spin)
        
        self.line_spacing_spin = QDoubleSpinBox()
        self.line_spacing_spin.setRange(1.0, 3.0)
        self.line_spacing_spin.setSingleStep(0.1)
        self.line_spacing_spin.setDecimals(1)
        font_layout.addRow("Line Spacing:", self.line_spacing_spin)
        
        # Margin rules group
        margin_group = QGroupBox("Margin Rules (cm)")
        margin_layout = QFormLayout(margin_group)
        
        self.margin_left_spin = QDoubleSpinBox()
        self.margin_left_spin.setRange(1.0, 10.0)
        self.margin_left_spin.setSingleStep(0.1)
        self.margin_left_spin.setDecimals(1)
        margin_layout.addRow("Left Margin:", self.margin_left_spin)
        
        self.margin_right_spin = QDoubleSpinBox()
        self.margin_right_spin.setRange(1.0, 10.0)
        self.margin_right_spin.setSingleStep(0.1)
        self.margin_right_spin.setDecimals(1)
        margin_layout.addRow("Right Margin:", self.margin_right_spin)
        
        self.margin_top_spin = QDoubleSpinBox()
        self.margin_top_spin.setRange(1.0, 10.0)
        self.margin_top_spin.setSingleStep(0.1)
        self.margin_top_spin.setDecimals(1)
        margin_layout.addRow("Top Margin:", self.margin_top_spin)
        
        self.margin_bottom_spin = QDoubleSpinBox()
        self.margin_bottom_spin.setRange(1.0, 10.0)
        self.margin_bottom_spin.setSingleStep(0.1)
        self.margin_bottom_spin.setDecimals(1)
        margin_layout.addRow("Bottom Margin:", self.margin_bottom_spin)
        
        self.margin_tolerance_spin = QDoubleSpinBox()
        self.margin_tolerance_spin.setRange(0.05, 0.5)
        self.margin_tolerance_spin.setSingleStep(0.05)
        self.margin_tolerance_spin.setDecimals(2)
        margin_layout.addRow("Tolerance (±):", self.margin_tolerance_spin)
        
        # Add groups to layout
        layout.addWidget(font_group)
        layout.addWidget(margin_group)
        layout.addStretch()
        
        return tab
        
    def _create_export_tab(self):
        """Create export settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export format group
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout(format_group)
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["PDF", "HTML", "TXT"])
        format_layout.addRow("Default format:", self.export_format_combo)
        
        self.include_details_check = QCheckBox("Include detailed issues")
        format_layout.addRow("", self.include_details_check)
        
        self.include_visual_check = QCheckBox("Include visual representation of issues")
        format_layout.addRow("", self.include_visual_check)
        
        # Add groups to layout
        layout.addWidget(format_group)
        layout.addStretch()
        
        return tab
        
    def _select_report_folder(self):
        """Open dialog to select report folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Reports Folder",
            self.report_folder_edit.text()
        )
        if folder:
            self.report_folder_edit.setText(folder)
            
    def _load_settings(self):
        """Load settings from QSettings"""
        # General settings
        self.theme_combo.setCurrentText(self.settings.value("theme", "System Default"))
        self.show_icons_check.setChecked(self.settings.value("show_icons", True, type=bool))
        self.auto_save_reports_check.setChecked(self.settings.value("auto_save_reports", False, type=bool))
        self.report_folder_edit.setText(self.settings.value("report_folder", ""))
        self.extensive_logging_check.setChecked(self.settings.value("developer/extensive_logging", False, type=bool))
        
        # Document rules
        self.font_name_edit.setText(self.settings.value("font_name", "Times New Roman"))
        self.font_size_spin.setValue(self.settings.value("font_size", 12.0, type=float))
        self.line_spacing_spin.setValue(self.settings.value("line_spacing", 1.5, type=float))
        
        self.margin_left_spin.setValue(self.settings.value("margin_left", 4.0, type=float))
        self.margin_right_spin.setValue(self.settings.value("margin_right", 3.0, type=float))
        self.margin_top_spin.setValue(self.settings.value("margin_top", 3.0, type=float))
        self.margin_bottom_spin.setValue(self.settings.value("margin_bottom", 3.0, type=float))
        self.margin_tolerance_spin.setValue(self.settings.value("margin_tolerance", 0.1, type=float))
        
        # Export settings
        self.export_format_combo.setCurrentText(self.settings.value("export_format", "PDF"))
        self.include_details_check.setChecked(self.settings.value("include_details", True, type=bool))
        self.include_visual_check.setChecked(self.settings.value("include_visual", True, type=bool))
        
    def _handle_theme_preview(self, theme_text):
        """Handle theme change preview if enabled"""
        if self.apply_theme_check.isChecked() and hasattr(self.parent_window, 'theme_manager'):
            # Temporarily save the previous theme value
            previous_theme = self.settings.value("theme", "System Default")
            
            # Save theme to settings temporarily
            self.settings.setValue("theme", theme_text)
            
            # Apply the theme
            self.parent_window.theme_manager.apply_theme()
            
            # Force an update of the UI
            self.repaint()
            
            # If user cancels, we'll restore the previous theme in reject()
        
    def _save_settings(self):
        """Save settings to QSettings"""
        # General settings
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("show_icons", self.show_icons_check.isChecked())
        self.settings.setValue("auto_save_reports", self.auto_save_reports_check.isChecked())
        self.settings.setValue("report_folder", self.report_folder_edit.text())
        self.settings.setValue("developer/extensive_logging", self.extensive_logging_check.isChecked())
        
        # Document rules
        self.settings.setValue("font_name", self.font_name_edit.text())
        self.settings.setValue("font_size", self.font_size_spin.value())
        self.settings.setValue("line_spacing", self.line_spacing_spin.value())
        
        self.settings.setValue("margin_left", self.margin_left_spin.value())
        self.settings.setValue("margin_right", self.margin_right_spin.value())
        self.settings.setValue("margin_top", self.margin_top_spin.value())
        self.settings.setValue("margin_bottom", self.margin_bottom_spin.value())
        self.settings.setValue("margin_tolerance", self.margin_tolerance_spin.value())
        
        # Export settings
        self.settings.setValue("export_format", self.export_format_combo.currentText())
        self.settings.setValue("include_details", self.include_details_check.isChecked())
        self.settings.setValue("include_visual", self.include_visual_check.isChecked())
        
        self.settings_changed.emit()
        self.accept()
        
    def _reset_settings(self):
        """Reset settings to defaults"""
        confirm = QMessageBox.question(
            self,
            "Reset Pengaturan",
            "Apakah Anda yakin ingin mereset semua pengaturan ke default?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Reset to defaults
            # General settings
            self.theme_combo.setCurrentText("System Default")
            self.show_icons_check.setChecked(True)
            self.auto_save_reports_check.setChecked(False)
            self.report_folder_edit.setText("")
            self.extensive_logging_check.setChecked(False)
            
            # Document rules
            self.font_name_edit.setText("Times New Roman")
            self.font_size_spin.setValue(12.0)
            self.line_spacing_spin.setValue(1.5)
            
            self.margin_left_spin.setValue(4.0)
            self.margin_right_spin.setValue(3.0)
            self.margin_top_spin.setValue(3.0)
            self.margin_bottom_spin.setValue(3.0)
            self.margin_tolerance_spin.setValue(0.1)
            
            # Export settings
            self.export_format_combo.setCurrentText("PDF")
            self.include_details_check.setChecked(True)
            self.include_visual_check.setChecked(True)
        
    def reject(self):
        """Override to restore theme if cancelled after preview"""
        if self.apply_theme_check.isChecked() and hasattr(self.parent_window, 'theme_manager'):
            # Restore original theme from before dialog was opened
            original_theme = self.settings.value("theme", "System Default")
            current_theme = self.theme_combo.currentText()
            
            # Only restore if they're different (user changed but canceled)
            if original_theme != current_theme:
                self.settings.setValue("theme", original_theme)
                self.parent_window.theme_manager.apply_theme()
                
        super().reject() 