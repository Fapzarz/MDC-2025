import os
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QAbstractItemView
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction, QColor
import darkdetect

# Define a custom role for storing file paths
FILE_PATH_ROLE = Qt.UserRole + 1

class FileListWidget(QListWidget):
    file_selected = Signal(str)  # Signal emitted when a file is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        
        # Adjust the style based on system theme
        self.is_dark_mode = darkdetect.isDark()
        self._set_style()
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemClicked.connect(self._on_item_clicked)
    
    def _set_style(self):
        """Set appropriate style based on system theme"""
        if self.is_dark_mode:
            self.setStyleSheet("""
                QListWidget {
                    border-radius: 8px;
                    border: 1px solid #2d323e;
                    padding: 8px;
                    background-color: #181c25;
                    font-size: 13px;
                }
                QListWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #2d323e;
                    border-radius: 6px;
                    margin: 2px 4px;
                }
                QListWidget::item:selected {
                    background-color: #334155;
                    color: #ffffff;
                }
                QListWidget::item:hover {
                    background-color: #1a1e27;
                }
            """)
        else:
            self.setStyleSheet("""
                QListWidget {
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                    padding: 8px;
                    background-color: #ffffff;
                    font-size: 13px;
                }
                QListWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #f1f5f9;
                    border-radius: 6px;
                    margin: 2px 4px;
                }
                QListWidget::item:selected {
                    background-color: #e0e7ff;
                    color: #4338ca;
                }
                QListWidget::item:hover {
                    background-color: #f1f5f9;
                }
            """)
        
    def add_files(self, file_paths):
        """Add files to the list widget"""
        for file_path in file_paths:
            # Check if file is already in the list
            for i in range(self.count()):
                if self.item(i).data(FILE_PATH_ROLE) == file_path:
                    break
            else:  # File not found in list
                filename = os.path.basename(file_path)
                ext = os.path.splitext(filename)[1].lower()
                
                item = QListWidgetItem(filename)
                # Store the file path in the item's data
                item.setData(FILE_PATH_ROLE, file_path)
                
                # Set different styling based on file type
                if ext == '.docx':
                    # We can add specific styling for DOCX files
                    if self.is_dark_mode:
                        item.setForeground(QColor("#a5b4fc"))  # Light purple in dark mode
                    else:
                        item.setForeground(QColor("#4f46e5"))  # Indigo in light mode
                    item.setIcon(QIcon("resources/icons/docx_icon.png"))
                elif ext == '.pdf':
                    # We can add specific styling for PDF files
                    if self.is_dark_mode:
                        item.setForeground(QColor("#bfdbfe"))  # Light blue in dark mode
                    else:
                        item.setForeground(QColor("#2563eb"))  # Blue in light mode
                    item.setIcon(QIcon("resources/icons/pdf_icon.png"))
                    
                self.addItem(item)
            
    def _on_item_clicked(self, item):
        """Handle item click to emit signal with file path"""
        file_path = item.data(FILE_PATH_ROLE)
        if file_path:
            self.file_selected.emit(file_path)
            
    def _show_context_menu(self, position):
        """Show context menu for list items"""
        item = self.itemAt(position)
        if not item:
            return
            
        context_menu = QMenu(self)
        context_menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 24px 8px 8px;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                background-color: #e0e7ff;
                color: #4338ca;
            }
        """)
        
        check_action = QAction("Check File", self)
        remove_action = QAction("Remove", self)
        remove_action.setIcon(QIcon("resources/icons/trash_icon.png"))
        
        check_action.triggered.connect(lambda: self._check_file(item))
        remove_action.triggered.connect(lambda: self._remove_file(item))
        
        context_menu.addAction(check_action)
        context_menu.addAction(remove_action)
        context_menu.exec(self.mapToGlobal(position))
        
    def _check_file(self, item):
        """Check the selected file"""
        file_path = item.data(FILE_PATH_ROLE)
        if file_path:
            self.file_selected.emit(file_path)
            
    def _remove_file(self, item):
        """Remove file from the list"""
        self.takeItem(self.row(item))
            
    def get_all_files(self):
        """Get all file paths in the list"""
        file_paths = []
        for i in range(self.count()):
            file_path = self.item(i).data(FILE_PATH_ROLE)
            if file_path:
                file_paths.append(file_path)
        return file_paths
        
    def clear(self):
        """Clear all items from the list"""
        super().clear() 