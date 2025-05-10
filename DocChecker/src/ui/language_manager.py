import os
from PySide6.QtCore import QObject, Signal, QSettings

class LanguageManager(QObject):
    """
    Centralized language manager for the application.
    Handles loading, switching, and applying language translations.
    """
    language_changed = Signal(str)  # Signal emitted when language changes
    
    def __init__(self, settings: QSettings):
        super().__init__()
        self.settings = settings
        self.current_language = "id"  # Default to Indonesian
        self.translations = {
            "id": self._load_indonesian(),
            "en": self._load_english()
        }
        
    def get_language(self) -> str:
        """
        Get the current language setting.
        Returns: "id" for Indonesian or "en" for English
        """
        return self.settings.value("language", "id")
    
    def apply_language(self):
        """
        Apply the current language to the application.
        """
        language = self.get_language()
        self.current_language = language
        
        # Emit signal for other components to react
        self.language_changed.emit(language)
        
        print(f"Language applied: {language}")
        return self.translations[language]
    
    def translate(self, key):
        """
        Get translation for specific key
        """
        language = self.get_language()
        if key in self.translations[language]:
            return self.translations[language][key]
        
        # Fallback to English if key not found
        if language != "en" and key in self.translations["en"]:
            return self.translations["en"][key]
            
        # Return the key itself if no translation found
        return key
    
    def _load_indonesian(self):
        """Load Indonesian translations"""
        return {
            # App title and general terms
            "app_title": "MetastroDocChecker 2025",
            "app_subtitle": "Validator Format Dokumen",
            "settings": "Pengaturan",
            "ready": "Siap",
            
            # Main UI sections
            "drag_drop": "Seret & Lepas",
            "drop_instruction": "Letakkan berkas DOCX atau PDF di sini\natau klik untuk memilih berkas",
            "selected_files": "Berkas Terpilih",
            "results": "Hasil",
            
            # Buttons
            "add_files": "Tambah Berkas",
            "clear_all": "Hapus Semua",
            "check_all_files": "Periksa Semua Berkas",
            
            # Results view
            "summary": "Ringkasan",
            "details": "Detail",
            "files": "Berkas",
            "no_document": "Belum Ada Dokumen Diperiksa",
            "select_file_instruction": "Pilih berkas dari daftar atau tambahkan berkas baru untuk diperiksa.",
            "document_check_results": "Hasil Pemeriksaan Dokumen",
            "file": "Berkas",
            "status": "Status",
            "passed": "LULUS",
            "failed": "GAGAL",
            "issues_summary": "Ringkasan Masalah",
            "font_issues": "Masalah Font",
            "font_size_issues": "Masalah Ukuran Font",
            "spacing_issues": "Masalah Spasi",
            "margin_issues": "Masalah Margin",
            "issue_type": "Jenis Masalah",
            "location": "Lokasi",
            "found": "Ditemukan",
            "expected": "Diharapkan",
            
            # Batch results
            "batch_check_results": "Hasil Pemeriksaan Batch",
            "total_files": "Total Berkas",
            "files_passed": "Berkas Lulus",
            "files_failed": "Berkas Bermasalah",
            "issues_found": "Masalah Ditemukan",
            "click_files_tab": "Klik tab \"Berkas\" untuk melihat detail setiap berkas.",
            
            # Settings dialog
            "settings_title": "Pengaturan Document Checker",
            "general": "Umum",
            "document_rules": "Aturan Dokumen",
            "export": "Ekspor",
            "interface": "Antarmuka",
            "theme": "Tema",
            "language": "Bahasa",
            "preview_changes": "Terapkan perubahan secara langsung",
            "show_file_icons": "Tampilkan ikon jenis berkas",
            "batch_processing": "Pemrosesan Batch",
            "auto_save_reports": "Simpan laporan otomatis setelah pemrosesan batch",
            "report_folder": "Folder laporan",
            "browse": "Jelajahi...",
            "developer": "Pengembang",
            "logging": "Pencatatan log",
            "enable_logging": "Aktifkan pencatatan log ekstensif",
            
            # Font rules
            "font_rules": "Aturan Font",
            "required_font": "Font yang Diperlukan",
            "font_size": "Ukuran Font (pt)",
            "line_spacing": "Spasi Baris",
            
            # Margin rules
            "margin_rules": "Aturan Margin (cm)",
            "left_margin": "Margin Kiri",
            "right_margin": "Margin Kanan",
            "top_margin": "Margin Atas",
            "bottom_margin": "Margin Bawah",
            "tolerance": "Toleransi (±)",
            
            # Export settings
            "export_format": "Format Ekspor",
            "default_format": "Format default",
            "include_details": "Sertakan detail masalah",
            "include_visual": "Sertakan representasi visual masalah",
            
            # Buttons
            "save_settings": "Simpan Pengaturan",
            "cancel": "Batal",
            "reset_defaults": "Kembalikan ke Default",
            
            # Reset settings confirmation
            "reset_title": "Reset Pengaturan",
            "reset_confirm": "Apakah Anda yakin ingin mereset semua pengaturan ke default?",
            
            # Dialog titles
            "select_documents": "Pilih Dokumen",
            "select_reports_folder": "Pilih Folder Laporan",
            "no_files": "Tidak Ada Berkas",
            "add_files_first": "Silakan tambahkan berkas untuk diperiksa terlebih dahulu.",
            "error": "Error",
            "checking_file": "Memeriksa: {filename}...",
            "failed_check": "Gagal memeriksa berkas: {error}",
            "batch_error": "Error Pemrosesan Batch",
            "batch_error_message": "Terjadi kesalahan saat memproses batch: {error}",
            "language_options": "Opsi Bahasa",
            "indonesian": "Bahasa Indonesia",
            "english": "Bahasa Inggris",
        }
    
    def _load_english(self):
        """Load English translations"""
        return {
            # App title and general terms
            "app_title": "MetastroDocChecker 2025",
            "app_subtitle": "Document Format Validator",
            "settings": "Settings",
            "ready": "Ready",
            
            # Main UI sections
            "drag_drop": "Drag & Drop",
            "drop_instruction": "Drop your DOCX or PDF files here\nor click to browse files",
            "selected_files": "Selected Files",
            "results": "Results",
            
            # Buttons
            "add_files": "Add Files",
            "clear_all": "Clear All",
            "check_all_files": "Check All Files",
            
            # Results view
            "summary": "Summary",
            "details": "Details",
            "files": "Files",
            "no_document": "No Document Checked Yet",
            "select_file_instruction": "Select a file from the list or add new files to check.",
            "document_check_results": "Document Check Results",
            "file": "File",
            "status": "Status",
            "passed": "PASSED",
            "failed": "FAILED",
            "issues_summary": "Issues Summary",
            "font_issues": "Font Issues",
            "font_size_issues": "Font Size Issues",
            "spacing_issues": "Spacing Issues",
            "margin_issues": "Margin Issues",
            "issue_type": "Issue Type",
            "location": "Location",
            "found": "Found",
            "expected": "Expected",
            
            # Batch results
            "batch_check_results": "Batch Check Results",
            "total_files": "Total Files",
            "files_passed": "Passed",
            "files_failed": "Failed",
            "issues_found": "Issues Found",
            "click_files_tab": "Click on the \"Files\" tab to see details for each file.",
            
            # Settings dialog
            "settings_title": "Document Checker Settings",
            "general": "General",
            "document_rules": "Document Rules",
            "export": "Export",
            "interface": "Interface",
            "theme": "Theme",
            "language": "Language",
            "preview_changes": "Preview changes immediately",
            "show_file_icons": "Show file type icons",
            "batch_processing": "Batch Processing",
            "auto_save_reports": "Auto-save reports after batch processing",
            "report_folder": "Report folder",
            "browse": "Browse...",
            "developer": "Developer",
            "logging": "Logging",
            "enable_logging": "Enable extensive logging",
            
            # Font rules
            "font_rules": "Font Rules",
            "required_font": "Required Font",
            "font_size": "Font Size (pt)",
            "line_spacing": "Line Spacing",
            
            # Margin rules
            "margin_rules": "Margin Rules (cm)",
            "left_margin": "Left Margin",
            "right_margin": "Right Margin",
            "top_margin": "Top Margin",
            "bottom_margin": "Bottom Margin",
            "tolerance": "Tolerance (±)",
            
            # Export settings
            "export_format": "Export Format",
            "default_format": "Default format",
            "include_details": "Include detailed issues",
            "include_visual": "Include visual representation of issues",
            
            # Buttons
            "save_settings": "Save Settings",
            "cancel": "Cancel",
            "reset_defaults": "Reset to Defaults",
            
            # Reset settings confirmation
            "reset_title": "Reset Settings",
            "reset_confirm": "Are you sure you want to reset all settings to default?",
            
            # Dialog titles
            "select_documents": "Select Documents",
            "select_reports_folder": "Select Reports Folder",
            "no_files": "No Files",
            "add_files_first": "Please add files to check first.",
            "error": "Error",
            "checking_file": "Checking: {filename}...",
            "failed_check": "Failed to check file: {error}",
            "batch_error": "Batch Processing Error",
            "batch_error_message": "An error occurred during batch processing: {error}",
            "language_options": "Language Options",
            "indonesian": "Bahasa Indonesia",
            "english": "English",
        } 