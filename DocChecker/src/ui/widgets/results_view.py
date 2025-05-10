from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QListWidget, QListWidgetItem, QScrollArea,
    QFrame, QSplitter, QGridLayout, QHeaderView, QStyle
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPalette, QIcon

import darkdetect
from core.document_checker import CheckResult

class ResultsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Detect if dark mode is enabled
        self.is_dark_mode = darkdetect.isDark()
        
        # Define color schemes based on mode
        self.colors = self._get_color_scheme()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)  # Mengurangi spasi antara elemen
        
        # Tabs for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(False)
        self.tab_widget.setDocumentMode(True)
        self.layout.addWidget(self.tab_widget)
        
        # Summary tab
        self.summary_tab = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_layout.setContentsMargins(5, 5, 5, 5)  # Mengurangi margin tab content
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        if self.is_dark_mode:
            # Use a dark background for the QTextEdit in dark mode
            self.summary_text.setStyleSheet("""
                QTextEdit {
                    background-color: #181c25;
                    color: #f0f2f5;
                    border: none;
                    border-radius: 8px;
                }
            """)
        self.summary_layout.addWidget(self.summary_text)
        
        # Files tab (for batch results)
        self.files_tab = QWidget()
        self.files_layout = QVBoxLayout(self.files_tab)
        self.files_layout.setContentsMargins(5, 5, 5, 5)  # Mengurangi margin tab content
        
        self.files_list = QListWidget()
        self.files_list.setAlternatingRowColors(True)
        self.files_list.itemClicked.connect(self._file_item_clicked)
        self.files_layout.addWidget(self.files_list)
        
        # Details tab
        self.details_tab = QWidget()
        self.details_layout = QVBoxLayout(self.details_tab)
        self.details_layout.setContentsMargins(5, 5, 5, 5)  # Mengurangi margin tab content
        
        # Issues table
        self.issues_table = QTableWidget(0, 4)  # Rows will be added as needed, 4 columns
        self.issues_table.setHorizontalHeaderLabels(["Issue Type", "Location", "Found", "Expected"])
        self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.issues_table.setAlternatingRowColors(True)
        if self.is_dark_mode:
            self.issues_table.setStyleSheet("""
                QTableWidget {
                    border: none;
                    border-radius: 8px;
                    font-size: 11pt;
                    background-color: #181c25;
                    color: #f0f2f5;
                }
                QHeaderView::section {
                    background-color: #1e2130;
                    padding: 6px;
                    font-weight: 600;
                    border: none;
                    border-bottom: 1px solid #2d323e;
                    color: #94a3b8;
                }
                QTableWidget::item {
                    padding: 6px;
                }
                QTableWidget::item:alternate {
                    background-color: #1a1e27;
                }
            """)
        else:
            self.issues_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 11pt;
                }
                QHeaderView::section {
                    background-color: #f1f5f9;
                    padding: 6px;
                    font-weight: 600;
                    border: none;
                    border-bottom: 1px solid #e2e8f0;
                    color: #64748b;
                }
                QTableWidget::item {
                    padding: 6px;
                }
                QTableWidget::item:alternate {
                    background-color: #f8fafc;
                }
            """)
        self.details_layout.addWidget(self.issues_table)
        
        # Add all tabs
        self.tab_widget.addTab(self.summary_tab, "Summary")
        self.tab_widget.addTab(self.details_tab, "Details")
        self.tab_widget.addTab(self.files_tab, "Files")
        
        # Connect tab changed signal to update content
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Initial empty state
        self.display_empty()
        
        # Track current result
        self.current_result = None
        self.batch_results = []
        
    def _get_color_scheme(self):
        """Return color scheme based on current theme"""
        if self.is_dark_mode:
            return {
                # Background colors
                'bg_main': "#0f1117",  # Updated for modern dark theme
                'bg_card': "#181c25", 
                'bg_success': "#1a2e1e",
                'bg_error': "#2e1e1e",
                
                # Text colors
                'text_primary': "#ffffff",
                'text_secondary': "#bbbbbb",
                
                # UI element colors
                'border': "#2d323e",
                'shadow': "rgba(0,0,0,0.5)",
                
                # Status colors
                'success': "#4caf50",
                'error': "#f44336",
                'warning': "#ff9800",
                'info': "#2196f3",
                
                # Issue type colors
                'font_issue': "#ff5252",
                'size_issue': "#ffab40",
                'spacing_issue': "#b2ff59",
                'margin_issue': "#40c4ff"
            }
        else:
            return {
                # Background colors
                'bg_main': "#f8fafc",  # Updated for modern light theme
                'bg_card': "#ffffff",
                'bg_success': "#f1f8e9",
                'bg_error': "#fef5f5",
                
                # Text colors
                'text_primary': "#1e293b",
                'text_secondary': "#64748b",
                
                # UI element colors
                'border': "#e2e8f0",
                'shadow': "rgba(0,0,0,0.12)",
                
                # Status colors
                'success': "#4caf50",
                'error': "#f44336",
                'warning': "#fb8c00",
                'info': "#039be5",
                
                # Issue type colors
                'font_issue': "#e53935",
                'size_issue': "#fb8c00",
                'spacing_issue': "#7cb342",
                'margin_issue': "#039be5"
            }
    
    def _on_tab_changed(self, index):
        """Handle tab changed event"""
        # Make sure the content is updated when switching tabs
        if index == 1 and self.current_result:  # Details tab
            self._update_details_table(self.current_result)
        
    def display_empty(self):
        """Display empty state"""
        colors = self.colors
        bg_color = colors['bg_card']
        text_color = colors['text_primary']
        text_secondary = colors['text_secondary']
        
        self.summary_text.setHtml(
            f"<div style='text-align:center; margin-top:50px;'>"
            f"<h2 style='margin-bottom:20px; color:{text_color};'>No Document Checked Yet</h2>"
            f"<p style='font-size:14px; color:{text_secondary};'>Select a file from the list or add new files to check.</p>"
            "</div>"
        )
        self.issues_table.setRowCount(0)
        self.files_list.clear()
        
    def display_result(self, result: CheckResult):
        """Display a single file check result"""
        self.current_result = result
        self.tab_widget.setCurrentIndex(0)  # Switch to summary tab
        
        colors = self.colors
        
        # Build summary HTML
        if result.success:
            status_color = colors['success']
            status_text = "PASSED"
            status_icon = "✓"
            bg_color = colors['bg_success']
        else:
            status_color = colors['error']
            status_text = "FAILED"
            status_icon = "✗"
            bg_color = colors['bg_error']
            
        # Count issue types
        font_issues = len(result.details.get("font_issues", []))
        size_issues = len(result.details.get("size_issues", []))
        spacing_issues = len(result.details.get("spacing_issues", []))
        margin_issues = len(result.details.get("margin_issues", []))
            
        summary_html = f"""
        <div style='background-color:{bg_color}; border-radius:8px; padding:15px; margin:0px;'>
            <h2 style='margin-top:5px; margin-bottom:15px; display:flex; align-items:center; color:{colors['text_primary']};'>
                <span style='display:inline-block; width:30px; height:30px; line-height:30px; 
                       border-radius:50%; text-align:center; background-color:{status_color}; 
                       color:{colors['bg_main']}; margin-right:10px; font-size:18px;'>{status_icon}</span>
                Document Check Results
            </h2>
            
            <div style='display:flex; flex-wrap:wrap; margin-bottom:15px;'>
                <div style='margin-right:30px;'>
                    <p style='margin:5px 0; color:{colors['text_secondary']};'>File</p>
                    <p style='margin:0; font-weight:bold; font-size:16px; color:{colors['text_primary']};'>{result.filename}</p>
                </div>
                <div>
                    <p style='margin:5px 0; color:{colors['text_secondary']};'>Status</p>
                    <p style='margin:0; font-weight:bold; font-size:16px; color:{status_color};'>{status_text}</p>
                </div>
            </div>
        """
        
        # Add issue summary cards if there are issues
        if not result.success:
            summary_html += f"""
            <h3 style='margin:20px 0 15px 0; color:{colors['text_primary']};'>Issues Summary</h3>
            <div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px;'>
            """
            
            # Font issues card
            if font_issues > 0:
                summary_html += f"""
                <div style='background-color:{colors['bg_card']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Font Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['font_issue']};'>{font_issues}</p>
                </div>
                """
                
            # Size issues card
            if size_issues > 0:
                summary_html += f"""
                <div style='background-color:{colors['bg_card']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Font Size Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['size_issue']};'>{size_issues}</p>
                </div>
                """
                
            # Spacing issues card
            if spacing_issues > 0:
                summary_html += f"""
                <div style='background-color:{colors['bg_card']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Spacing Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['spacing_issue']};'>{spacing_issues}</p>
                </div>
                """
                
            # Margin issues card
            if margin_issues > 0:
                summary_html += f"""
                <div style='background-color:{colors['bg_card']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Margin Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['margin_issue']};'>{margin_issues}</p>
                </div>
                """
                
            summary_html += "</div>"  # End of cards container
            
            # Add detailed issues list
            summary_html += f"""
            <h3 style='margin:20px 0 15px 0; color:{colors['text_primary']};'>Details</h3>
            <div style='background-color:{colors['bg_card']}; border-radius:4px; padding:15px;
                     box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
        """
        
        if not result.messages:
            summary_html += f"<p style='color:{colors['text_secondary']};'><i>No issues found.</i></p>"
        else:
            summary_html += f"<ul style='margin:0; padding-left:20px; color:{colors['text_primary']};'>"
            for msg in result.messages:
                # Determine icon and color based on issue type
                if "Font tidak sesuai" in msg:
                    icon = "🔤"
                    color = colors['font_issue']
                elif "Ukuran font" in msg:
                    icon = "📏"
                    color = colors['size_issue']
                elif "Spasi tidak sesuai" in msg:
                    icon = "↕️"
                    color = colors['spacing_issue']
                elif "Margin" in msg:
                    icon = "📄"
                    color = colors['margin_issue']
                else:
                    icon = "ℹ️"
                    color = colors['text_secondary']
                
                summary_html += f"""
                <li style='margin-bottom:8px;'>
                    <span style='margin-right:8px; font-size:14px;'>{icon}</span>
                    <span style='color:{color};'>{msg}</span>
                </li>
                """
            summary_html += "</ul>"
                
        summary_html += """
        </div>
        """
        
        summary_html += """
        </div>
        """
        
        self.summary_text.setHtml(summary_html)
        
        # Update details tab
        self._update_details_table(result)
        
    def display_batch_summary(self, summary_html, results):
        """Display batch check results"""
        self.batch_results = results
        self.current_result = None
        self.tab_widget.setCurrentIndex(0)  # Switch to summary tab
        
        colors = self.colors
        
        # Count total issues by type
        total_font_issues = sum(len(r.details.get("font_issues", [])) for r in results)
        total_size_issues = sum(len(r.details.get("size_issues", [])) for r in results)
        total_spacing_issues = sum(len(r.details.get("spacing_issues", [])) for r in results)
        total_margin_issues = sum(len(r.details.get("margin_issues", [])) for r in results)
        
        # Count successful and failed files
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed
        
        # Create modern HTML for batch summary
        batch_html = f"""
        <div style='background-color:{colors['bg_card']}; border-radius:8px; padding:15px; margin:0px;'>
            <h2 style='margin-top:5px; margin-bottom:15px; color:{colors['text_primary']};'>Batch Check Results</h2>
            
            <div style='display:flex; flex-wrap:wrap; gap:15px; margin-bottom:20px;'>
                <div style='background-color:{colors['bg_main']}; border-radius:4px; padding:15px; min-width:150px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Total Files</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['text_primary']};'>{len(results)}</p>
                </div>
                
                <div style='background-color:{colors['bg_main']}; border-radius:4px; padding:15px; min-width:150px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Passed</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['success']};'>{passed}</p>
                </div>
                
                <div style='background-color:{colors['bg_main']}; border-radius:4px; padding:15px; min-width:150px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Failed</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['error']};'>{failed}</p>
                </div>
            </div>
            
            <h3 style='margin:20px 0 15px 0; color:{colors['text_primary']};'>Issues Found</h3>
            
            <div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px;'>
                <div style='background-color:{colors['bg_main']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Font Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['font_issue']};'>{total_font_issues}</p>
                </div>
                
                <div style='background-color:{colors['bg_main']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Font Size Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['size_issue']};'>{total_size_issues}</p>
                </div>
                
                <div style='background-color:{colors['bg_main']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Spacing Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['spacing_issue']};'>{total_spacing_issues}</p>
                </div>
                
                <div style='background-color:{colors['bg_main']}; border-radius:4px; padding:12px; min-width:120px;
                         box-shadow:0 1px 3px {colors['shadow']}, 0 1px 2px {colors['shadow']};'>
                    <p style='margin:0 0 5px 0; color:{colors['text_secondary']}; font-size:12px;'>Margin Issues</p>
                    <p style='margin:0; font-weight:bold; font-size:24px; color:{colors['margin_issue']};'>{total_margin_issues}</p>
                </div>
            </div>
            
            <p style='margin:30px 0 10px 0; color:{colors['text_secondary']};'>Click on the "Files" tab to see details for each file.</p>
        </div>
        """
        
        self.summary_text.setHtml(batch_html)
        
        # Update files list
        self.files_list.clear()
        for result in results:
            item = QListWidgetItem(result.filename)
            if result.success:
                if self.is_dark_mode:
                    item.setBackground(QColor(39, 55, 41))  # Dark green
                else:
                    item.setBackground(QColor(232, 245, 233))  # Light green
                item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
            else:
                if self.is_dark_mode:
                    item.setBackground(QColor(55, 39, 40))  # Dark red
                else:
                    item.setBackground(QColor(255, 235, 238))  # Light red
                item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
            self.files_list.addItem(item)
            
        # Clear details table
        self.issues_table.setRowCount(0)
        
    def _file_item_clicked(self, item):
        """Handle file item click in batch results view"""
        index = self.files_list.row(item)
        if 0 <= index < len(self.batch_results):
            result = self.batch_results[index]
            self.display_result(result)
            
    def _update_details_table(self, result: CheckResult):
        """Update the details table with issues"""
        self.issues_table.setRowCount(0)
        
        if not result.details:
            return
            
        row = 0
        
        # Font issues
        for issue in result.details.get("font_issues", []):
            self.issues_table.insertRow(row)
            
            type_item = QTableWidgetItem("Font")
            type_item.setForeground(QColor(self.colors['font_issue']))
            self.issues_table.setItem(row, 0, type_item)
            
            if "paragraph" in issue:
                location = f"Paragraph {issue['paragraph'] + 1}"
                if issue.get("text"):
                    # Show truncated text for context
                    text = issue.get("text")
                    if len(text) > 20:
                        text = text[:20] + "..."
                    location += f"\n\"{text}\""
            elif "page" in issue:
                location = f"Page {issue['page']}"
            else:
                location = "Unknown"
                
            self.issues_table.setItem(row, 1, QTableWidgetItem(location))
            
            found_item = QTableWidgetItem(str(issue.get("found", "Unknown")))
            found_item.setForeground(QColor(self.colors['font_issue']))
            self.issues_table.setItem(row, 2, found_item)
            
            expected_item = QTableWidgetItem(str(issue.get("expected", "Unknown")))
            expected_item.setForeground(QColor(self.colors['success']))
            self.issues_table.setItem(row, 3, expected_item)
            
            row += 1
            
        # Size issues
        for issue in result.details.get("size_issues", []):
            self.issues_table.insertRow(row)
            
            type_item = QTableWidgetItem("Font Size")
            type_item.setForeground(QColor(self.colors['size_issue']))
            self.issues_table.setItem(row, 0, type_item)
            
            if "paragraph" in issue:
                location = f"Paragraph {issue['paragraph'] + 1}"
                if issue.get("text"):
                    # Show truncated text for context
                    text = issue.get("text")
                    if len(text) > 20:
                        text = text[:20] + "..."
                    location += f"\n\"{text}\""
            elif "page" in issue:
                location = f"Page {issue['page']}"
            else:
                location = "Unknown"
                
            self.issues_table.setItem(row, 1, QTableWidgetItem(location))
            
            found_item = QTableWidgetItem(f"{issue.get('found', 'Unknown')} pt")
            found_item.setForeground(QColor(self.colors['size_issue']))
            self.issues_table.setItem(row, 2, found_item)
            
            expected_item = QTableWidgetItem(f"{issue.get('expected', 'Unknown')} pt")
            expected_item.setForeground(QColor(self.colors['success']))
            self.issues_table.setItem(row, 3, expected_item)
            
            row += 1
            
        # Spacing issues
        for issue in result.details.get("spacing_issues", []):
            self.issues_table.insertRow(row)
            
            type_item = QTableWidgetItem("Line Spacing")
            type_item.setForeground(QColor(self.colors['spacing_issue']))
            self.issues_table.setItem(row, 0, type_item)
            
            location = f"Paragraph {issue.get('paragraph', 0) + 1}"
            if issue.get("text"):
                # Show truncated text for context
                text = issue.get("text")
                if len(text) > 20:
                    text = text[:20] + "..."
                location += f"\n\"{text}\""
                
            self.issues_table.setItem(row, 1, QTableWidgetItem(location))
            
            found_item = QTableWidgetItem(str(issue.get("found", "Unknown")))
            found_item.setForeground(QColor(self.colors['spacing_issue']))
            self.issues_table.setItem(row, 2, found_item)
            
            expected_item = QTableWidgetItem(str(issue.get("expected", "Unknown")))
            expected_item.setForeground(QColor(self.colors['success']))
            self.issues_table.setItem(row, 3, expected_item)
            
            row += 1
            
        # Margin issues
        for issue in result.details.get("margin_issues", []):
            self.issues_table.insertRow(row)
            
            type_item = QTableWidgetItem("Margin")
            type_item.setForeground(QColor(self.colors['margin_issue']))
            self.issues_table.setItem(row, 0, type_item)
            
            margin_loc = issue.get("margin", "unknown").capitalize()
            self.issues_table.setItem(row, 1, QTableWidgetItem(margin_loc))
            
            found_item = QTableWidgetItem(f"{issue.get('found', 0):.2f} cm")
            found_item.setForeground(QColor(self.colors['margin_issue']))
            self.issues_table.setItem(row, 2, found_item)
            
            expected_item = QTableWidgetItem(f"{issue.get('expected', 0):.2f} cm")
            expected_item.setForeground(QColor(self.colors['success']))
            self.issues_table.setItem(row, 3, expected_item)
            
            row += 1 

    def update_theme(self, is_dark_mode):
        """Update theme for this widget"""
        self.is_dark_mode = is_dark_mode
        self.colors = self._get_color_scheme()
        
        # Update the QTextEdit style for the summary
        if self.is_dark_mode:
            self.summary_text.setStyleSheet("""
                QTextEdit {
                    background-color: #181c25;
                    color: #f0f2f5;
                    border: none;
                    border-radius: 8px;
                }
            """)
        else:
            self.summary_text.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #1e293b;
                    border: none;
                    border-radius: 8px;
                }
            """)
            
        # Update the issues table style
        if self.is_dark_mode:
            self.issues_table.setStyleSheet("""
                QTableWidget {
                    border: none;
                    border-radius: 8px;
                    font-size: 11pt;
                    background-color: #181c25;
                    color: #f0f2f5;
                }
                QHeaderView::section {
                    background-color: #1e2130;
                    padding: 6px;
                    font-weight: 600;
                    border: none;
                    border-bottom: 1px solid #2d323e;
                    color: #94a3b8;
                }
                QTableWidget::item {
                    padding: 6px;
                }
                QTableWidget::item:alternate {
                    background-color: #1a1e27;
                }
            """)
        else:
            self.issues_table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 11pt;
                    background-color: #ffffff;
                    color: #1e293b;
                }
                QHeaderView::section {
                    background-color: #f1f5f9;
                    padding: 6px;
                    font-weight: 600;
                    border: none;
                    border-bottom: 1px solid #e2e8f0;
                    color: #64748b;
                }
                QTableWidget::item {
                    padding: 6px;
                }
                QTableWidget::item:alternate {
                    background-color: #f8fafc;
                }
            """)
            
        # Update the list widget style
        if self.is_dark_mode:
            self.files_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #2d323e;
                    border-radius: 8px;
                    background-color: #181c25;
                    alternate-background-color: #1a1e27;
                    color: #f0f2f5;
                    padding: 8px;
                }
                QListWidget::item {
                    padding: 12px;
                    border-bottom: 1px solid #2d323e;
                    border-radius: 6px;
                    margin: 2px 4px;
                }
                QListWidget::item:selected {
                    background-color: #334155;
                    color: #ffffff;
                }
                QListWidget::item:hover:!selected {
                    background-color: #1a1e27;
                }
            """)
        else:
            self.files_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background-color: #ffffff;
                    alternate-background-color: #f8fafc;
                    color: #1e293b;
                    padding: 8px;
                }
                QListWidget::item {
                    padding: 12px;
                    border-bottom: 1px solid #f1f5f9;
                    border-radius: 6px;
                    margin: 2px 4px;
                }
                QListWidget::item:selected {
                    background-color: #e0e7ff;
                    color: #4338ca;
                }
                QListWidget::item:hover:!selected {
                    background-color: #f1f5f9;
                }
            """)
        
        # Update the tab widget style
        if self.is_dark_mode:
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #2d323e;
                    border-radius: 8px;
                    background-color: #181c25;
                }
                QTabBar::tab {
                    background-color: #0f1117;
                    border: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 10px 20px;
                    margin-right: 4px;
                    color: #94a3b8;
                    font-weight: 500;
                }
                QTabBar::tab:selected {
                    background-color: #181c25;
                    color: #f0f2f5;
                    border-bottom: 2px solid #6366f1;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #1a1e27;
                    color: #cbd5e1;
                }
            """)
        else:
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f8fafc;
                    border: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 10px 20px;
                    margin-right: 4px;
                    color: #64748b;
                    font-weight: 500;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    color: #0f172a;
                    border-bottom: 2px solid #6366f1;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #f1f5f9;
                    color: #334155;
                }
            """)
        
        # If there's a current result, redisplay it with the new theme
        if self.current_result:
            self.display_result(self.current_result)
        # If there are batch results, redisplay them
        elif self.batch_results:
            self.display_batch_summary("", self.batch_results)
        else:
            # Display empty state with updated colors
            self.display_empty() 