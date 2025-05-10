from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal, Slot, QSize

class BatchProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Memproses File")
        self.setMinimumWidth(500)
        self.setMinimumHeight(150)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Status label
        self.status_label = QLabel("Memproses file...")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Progress bar dengan style modern
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFormat("%v dari %m (%p%)")
        
        # Current file label
        self.file_label = QLabel("")
        self.file_label.setAlignment(Qt.AlignCenter)
        
        # Cancel button
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Batalkan")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.file_label)
        layout.addLayout(button_layout)
        
    def set_total(self, total):
        """Set the total number of files to process"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
        
    @Slot(int, int, str)
    def update_progress(self, current, total, filename=""):
        """Update progress bar and labels"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Memproses file {current} dari {total}")
        
        if filename:
            self.file_label.setText(f"File saat ini: {filename}")
        
        # Auto-close if completed
        if current >= total:
            self.accept() 