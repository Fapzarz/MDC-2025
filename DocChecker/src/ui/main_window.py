import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QProgressBar,
    QListWidget, QListWidgetItem, QTabWidget, QSplitter,
    QGroupBox, QTextEdit, QMessageBox, QFrame, QScrollArea
)
from PySide6.QtCore import (
    Qt, QSize, Signal, Slot, QThread, QMimeData, 
    QRunnable, QThreadPool, QObject, QMetaObject,
    QCoreApplication, QSettings
)
from PySide6.QtGui import QFont, QIcon, QDrag, QDragEnterEvent, QDropEvent

from ui.widgets.file_list_widget import FileListWidget
from ui.widgets.results_view import ResultsView
from ui.widgets.settings_dialog import SettingsDialog
from ui.widgets.batch_progress_dialog import BatchProgressDialog

from core.document_checker import DocumentChecker, CheckResult
from core.logger_config import setup_logging
import logging

logger = logging.getLogger(__name__)

# Worker class untuk menangani pemrosesan batch dalam thread terpisah
class BatchProcessWorker(QRunnable):
    """
    Worker thread untuk memproses batch dokumen.
    
    Menggunakan QRunnable untuk kompatibilitas dengan QThreadPool, yang
    menyediakan manajemen thread yang lebih baik dibandingkan QThread langsung.
    """
    
    class WorkerSignals(QObject):
        """
        Mendefinisikan sinyal yang tersedia dari worker thread.
        """
        progress = Signal(int, int, str)  # current, total, current_filename
        result = Signal(object)  # hasil pemeriksaan
        finished = Signal(list)  # semua hasil batch
        error = Signal(str)  # pesan error
        
    def __init__(self, document_checker, file_paths):
        super().__init__()
        self.signals = self.WorkerSignals()
        self.document_checker = document_checker
        self.file_paths = file_paths
        self.is_cancelled = False
        
    def run(self):
        """
        Menjalankan worker thread.
        """
        results = []
        total = len(self.file_paths)
        
        try:
            for i, file_path in enumerate(self.file_paths):
                if self.is_cancelled:
                    break
                    
                # Eksekusi pada thread utama - kirim nama file saat ini ke progress dialog
                current_filename = os.path.basename(file_path)
                self.signals.progress.emit(i, total, current_filename)
                
                try:
                    # Periksa file
                    result = self.document_checker.check_file(file_path)
                    results.append(result)
                    self.signals.result.emit(result)
                    
                    # Update progress
                    self.signals.progress.emit(i + 1, total, current_filename)
                except Exception as e:
                    error_result = CheckResult(
                        filename=os.path.basename(file_path),
                        success=False,
                        messages=[f"Error: {str(e)}"]
                    )
                    results.append(error_result)
                    self.signals.result.emit(error_result)
                    self.signals.progress.emit(i + 1, total, current_filename)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            # Selesai, kirim sinyal selesai dengan semua hasil
            self.signals.finished.emit(results)
    
    def cancel(self):
        """
        Set flag untuk membatalkan operasi.
        """
        self.is_cancelled = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize QSettings
        self.settings = QSettings("MDC-2025", "Document Checker")
        
        # theme_manager will be set by main.py
        self.theme_manager = None
        
        # Setup logging based on settings
        setup_logging(self.settings)
        logger.info("Aplikasi MetastroDocChecker 2025 dimulai.")
        
        # Create DocumentChecker with settings
        self.document_checker = DocumentChecker(self.settings)
        self.old_document_checker = None # Untuk menyimpan referensi lama saat settings berubah
        
        self.thread_pool = QThreadPool.globalInstance()
        # Mengatur jumlah maksimum thread berdasarkan jumlah core CPU
        optimal_thread_count = max(2, QThreadPool.globalInstance().maxThreadCount() // 2)
        self.thread_pool.setMaxThreadCount(optimal_thread_count)
        
        self.current_worker = None
        
        self.setWindowTitle("MetastroDocChecker 2025 (MDC-2025)")
        self.setMinimumSize(1000, 700)
        
        # Setup central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)
        
        # Setup header section
        self._setup_header()
        
        # Setup main content - drop area and file list
        self.content_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.content_splitter, 1)
        
        # Left panel - file list and controls
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 10, 0)
        self._setup_file_panel()
        
        # Right panel - results view
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(10, 0, 0, 0)
        self._setup_results_panel()
        
        # Add panels to splitter
        self.content_splitter.addWidget(self.left_panel)
        self.content_splitter.addWidget(self.right_panel)
        self.content_splitter.setSizes([300, 700])
        
        # Setup status bar at the bottom
        self.statusBar().showMessage("Siap")
        
        # Connect signals
        self._connect_signals()
        
        # Store batch results
        self.batch_results = []
        
    def _setup_header(self):
        """Setup the header section with logo and title"""
        logger.debug("Setup header UI.")
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        # Modern logo treatment
        logo_label = QLabel("📑")
        logo_label.setFont(QFont("Segoe UI", 26))
        logo_label.setStyleSheet("color: #6366f1;")
        
        # Title with modern styling
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        title_label = QLabel("MetastroDocChecker")
        title_label.setObjectName("heading")
        title_label.setStyleSheet("font-size: 22px; font-weight: 600; margin: 0; padding: 0;")
        
        subtitle_label = QLabel("Document Format Validator")
        subtitle_label.setObjectName("subheading")
        subtitle_label.setStyleSheet("color: #64748b; font-size: 14px; font-weight: 400; margin: 0; padding: 0;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_widget)
        header_layout.addStretch(1)
        
        # Modern settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setObjectName("secondary")
        settings_btn.clicked.connect(self._show_settings)
        settings_btn.setMinimumHeight(36)
        settings_btn.setMaximumWidth(120)
        header_layout.addWidget(settings_btn)
        
        self.main_layout.addWidget(header_widget)
        
        # Add horizontal separator line with more subtle styling
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        self.separator = separator  # Store reference for theme updates
        
        # We'll set the color dynamically in _update_theme_elements
        separator.setStyleSheet("background-color: #e2e8f0; border: none; height: 1px; margin: 0 0 10px 0;")
        self.main_layout.addWidget(separator)
        
    def _setup_file_panel(self):
        """Setup the left panel with file drop area and controls"""
        logger.debug("Setup panel file UI.")
        # File drop area group with modern styling
        drop_group = QGroupBox("Drag & Drop")
        drop_group.setStyleSheet("QGroupBox { font-weight: 600; font-size: 14px; }")
        drop_layout = QVBoxLayout(drop_group)
        
        self.drop_area = QLabel("Drop your DOCX or PDF files here\nor click to browse files")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #cbd5e1;
                border-radius: 8px;
                padding: 30px;
                background-color: #f8fafc;
                color: #64748b;
                font-size: 13px;
            }
        """)
        self.drop_area.setAcceptDrops(True)
        self.drop_area.mousePressEvent = self._open_file_dialog
        drop_layout.addWidget(self.drop_area)
        
        # File list group with modern styling
        file_group = QGroupBox("Selected Files")
        file_group.setStyleSheet("QGroupBox { font-weight: 600; font-size: 14px; }")
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = FileListWidget()
        file_layout.addWidget(self.file_list)
        
        # Buttons for file operations with modern styling
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.add_file_btn = QPushButton("Add Files")
        self.add_file_btn.setObjectName("secondary")
        self.add_file_btn.clicked.connect(self._open_file_dialog)
        
        self.clear_files_btn = QPushButton("Clear All")
        self.clear_files_btn.setObjectName("secondary")
        self.clear_files_btn.clicked.connect(self.file_list.clear)
        
        btn_layout.addWidget(self.add_file_btn)
        btn_layout.addWidget(self.clear_files_btn)
        file_layout.addLayout(btn_layout)
        
        self.check_files_btn = QPushButton("Check All Files")
        self.check_files_btn.clicked.connect(self._check_all_files)
        file_layout.addWidget(self.check_files_btn)
        
        # Add to left panel
        self.left_layout.addWidget(drop_group)
        self.left_layout.addWidget(file_group, 1)
        
    def _setup_results_panel(self):
        """Setup the right panel with results view"""
        logger.debug("Setup panel hasil UI.")
        results_group = QGroupBox("Results")
        results_group.setStyleSheet("QGroupBox { font-weight: 600; font-size: 14px; }")
        results_layout = QVBoxLayout(results_group)
        
        self.results_view = ResultsView()
        results_layout.addWidget(self.results_view)
        
        self.right_layout.addWidget(results_group)
        
    def _connect_signals(self):
        """Connect all signals between components"""
        logger.debug("Menghubungkan sinyal antar komponen.")
        # File list signals
        self.file_list.file_selected.connect(self._check_selected_file)
        
        # Document checker signals
        if self.document_checker:
            self.document_checker.check_completed.connect(self.results_view.display_result)
            
        # Connect theme manager signals if available
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._handle_theme_changed)
        
    def _disconnect_old_signals(self):
        """Disconnect signals from the old document_checker instance."""
        if self.old_document_checker:
            try:
                self.old_document_checker.check_completed.disconnect(self.results_view.display_result)
            except RuntimeError:
                pass # Signal was not connected or already disconnected
            self.old_document_checker = None
        
    def _open_file_dialog(self, event=None):
        """Open file dialog to select documents"""
        logger.debug("Membuka dialog file.")
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Pilih Dokumen",
            "",
            "Dokumen (*.docx *.pdf)"
        )
        
        if file_paths:
            self.file_list.add_files(file_paths)
            logger.info(f"{len(file_paths)} file ditambahkan dari dialog.")
            
    def _check_selected_file(self, file_path):
        """Check a single selected file"""
        if not file_path:
            logger.debug("Pemilihan file dibatalkan atau path kosong, pemeriksaan dilewati.")
            return
            
        self.statusBar().showMessage(f"Memeriksa: {os.path.basename(file_path)}...")
        logger.info(f"Memulai pemeriksaan untuk file terpilih: {file_path}")
        
        try:
            result = self.document_checker.check_file(file_path)
            self.results_view.display_result(result)
        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Gagal memeriksa file: {str(e)}")
            logger.exception(f"Error saat memeriksa file tunggal {file_path}")
        
        self.statusBar().showMessage("Siap")
        logger.info(f"Pemeriksaan file tunggal selesai: {file_path}")
        
    def _check_all_files(self):
        """Check all files in the list"""
        file_paths = self.file_list.get_all_files()
        if not file_paths:
            logger.info("Tidak ada file dalam daftar untuk diperiksa (batch).")
            QMessageBox.information(
                self,
                "Tidak Ada File",
                "Silakan tambahkan file untuk diperiksa terlebih dahulu."
            )
            return
            
        logger.info(f"Memulai pemeriksaan batch untuk {len(file_paths)} file.")
        # Show progress dialog
        self.progress_dialog = BatchProgressDialog(self)
        self.progress_dialog.set_total(len(file_paths))
        
        # Connect dialog cancel signal
        self.progress_dialog.rejected.connect(self._cancel_batch_processing)
        
        # Create worker and connect signals
        self.batch_results = []
        self.current_worker = BatchProcessWorker(self.document_checker, file_paths)
        self.current_worker.signals.progress.connect(self.progress_dialog.update_progress)
        self.current_worker.signals.result.connect(self._process_batch_result)
        self.current_worker.signals.finished.connect(self._batch_check_completed)
        self.current_worker.signals.error.connect(self._handle_batch_error)
        
        # Start processing in thread pool
        self.thread_pool.start(self.current_worker)
        
        # Show dialog
        self.progress_dialog.exec()
        
    def _cancel_batch_processing(self):
        """Cancel the current batch processing"""
        if self.current_worker:
            self.current_worker.cancel()
            logger.info("Pemrosesan batch dibatalkan oleh pengguna.")
            self.statusBar().showMessage("Pemrosesan batch dibatalkan")
        
    def _process_batch_result(self, result):
        """Process a single result from batch processing"""
        logger.debug(f"Menerima hasil batch untuk: {result.filename}, Sukses: {result.success}")
        self.batch_results.append(result)
        
    def _handle_batch_error(self, error_message):
        """Handle batch processing error"""
        logger.error(f"Error selama pemrosesan batch: {error_message}")
        QMessageBox.critical(
            self,
            "Error Pemrosesan Batch",
            f"Terjadi kesalahan saat memproses batch: {error_message}"
        )
        
    def _batch_check_completed(self, results):
        """Handle batch check completion"""
        logger.info(f"Pemrosesan batch selesai. Jumlah hasil: {len(results)}")
        # Update status and results
        self.current_worker = None
        self.statusBar().showMessage(f"Selesai memeriksa {len(results)} file")
        
        # If no results (canceled), do nothing
        if not results:
            return
            
        # Display summary
        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count
        
        summary = (
            f"<h3>Hasil Pemeriksaan Batch</h3>"
            f"<p>Total file diperiksa: <b>{len(results)}</b></p>"
            f"<p>File lulus: <b>{success_count}</b></p>"
            f"<p>File dengan masalah: <b>{fail_count}</b></p>"
        )
        
        self.results_view.display_batch_summary(summary, results)
        
    def _show_settings(self):
        """Show the settings dialog"""
        logger.debug("Membuka dialog pengaturan.")
        dialog = SettingsDialog(self.settings, self) # Pass QSettings instance
        dialog.settings_changed.connect(self._handle_settings_changed)
        dialog.exec()
        
    @Slot()
    def _handle_settings_changed(self):
        """Re-initialize DocumentChecker and reconnect signals when settings change."""
        logger.info("Pengaturan diubah. Menginisialisasi ulang DocumentChecker dan konfigurasi logging.")
        self.old_document_checker = self.document_checker # Simpan referensi lama
        self.document_checker = DocumentChecker(self.settings) # Buat instance baru
        
        self._disconnect_old_signals() # Putuskan koneksi dari instance lama
        self._connect_signals() # Hubungkan sinyal ke instance baru
        
        # Re-setup logging based on potentially changed settings
        setup_logging(self.settings)
        logger.info("Pengaturan diperbarui, logging dikonfigurasi ulang jika perlu.")
        
        # Apply theme if theme manager is available
        if self.theme_manager:
            self.theme_manager.apply_theme()
        
        self.statusBar().showMessage("Settings saved and applied.", 3000)
        
    def _handle_theme_changed(self, theme: str):
        """Handle theme change event"""
        logger.info(f"Theme changed to: {theme}")
        
        # Update theme-dependent UI elements
        self._update_theme_elements()
        
        # Force file list widget to update its style
        if hasattr(self, "file_list") and hasattr(self.file_list, "_set_style"):
            self.file_list.is_dark_mode = self.theme_manager.is_dark_mode()
            self.file_list._set_style()
            
        # Update results view if it exists
        if hasattr(self, "results_view"):
            is_dark = self.theme_manager.is_dark_mode()
            
            # Use explicit update_theme method if available
            if hasattr(self.results_view, "update_theme"):
                self.results_view.update_theme(is_dark)
            # Otherwise fall back to updating properties directly
            elif hasattr(self.results_view, "_get_color_scheme"):
                self.results_view.is_dark_mode = is_dark
                self.results_view.colors = self.results_view._get_color_scheme()
            
            # Update any current display in results view
            if hasattr(self.results_view, "current_result") and self.results_view.current_result:
                self.results_view.display_result(self.results_view.current_result)
            elif hasattr(self.results_view, "batch_results") and self.results_view.batch_results:
                self.results_view.display_batch_summary("", self.results_view.batch_results)
            
        # Force complete UI refresh
        self.repaint()
            
        self.statusBar().showMessage(f"Theme changed to {theme}", 3000)
    
    def _update_theme_elements(self):
        """Update UI elements that need special handling for theme changes"""
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        
        # Update separator color
        if hasattr(self, "separator"):
            separator_color = "#2d323e" if is_dark else "#e2e8f0"
            self.separator.setStyleSheet(f"background-color: {separator_color}; border: none; height: 1px; margin: 0 0 10px 0;")
        
        # Update drop area style
        if hasattr(self, "drop_area"):
            border_color = "#2d323e" if is_dark else "#cbd5e1"
            bg_color = "#181c25" if is_dark else "#f8fafc"
            text_color = "#94a3b8" if is_dark else "#64748b"
            
            self.drop_area.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {border_color};
                    border-radius: 8px;
                    padding: 30px;
                    background-color: {bg_color};
                    color: {text_color};
                    font-size: 13px;
                }}
            """)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for file drops"""
        if event.mimeData().hasUrls():
            logger.debug("Drag enter event diterima dengan URLs.")
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """Handle drop event for files"""
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext in ['.docx', '.pdf']:
                        file_paths.append(file_path)
                    else:
                        logger.debug(f"File yang di-drop dilewati (ekstensi tidak didukung): {file_path}")
                        
            if file_paths:
                self.file_list.add_files(file_paths)
                logger.info(f"{len(file_paths)} file di-drop dan ditambahkan ke daftar.")
            event.acceptProposedAction() 