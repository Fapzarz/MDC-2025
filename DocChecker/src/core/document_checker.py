import os
import io
from docx import Document
import fitz  # PyMuPDF
from typing import Dict, List, Tuple, Union, Any, Optional
from PySide6.QtCore import QObject, Signal, QSettings
import logging # Impor modul logging

logger = logging.getLogger(__name__) # Buat logger khusus untuk modul ini

class CheckResult:
    def __init__(self, filename: str, success: bool, messages: List[str], details: Dict[str, Any] = None):
        self.filename = filename
        self.success = success
        self.messages = messages
        self.details = details or {}

class DocumentChecker(QObject):
    check_completed = Signal(object)  # Emits CheckResult
    progress_updated = Signal(int, int)  # current, total
    batch_completed = Signal(list)  # List[CheckResult]
    
    def __init__(self, settings: QSettings):
        super().__init__()
        self.settings = settings
        logger.info("DocumentChecker diinisialisasi.")
        
    def _get_setting(self, key: str, default: Any, type: type = None):
        """Helper to get setting with type conversion."""
        value = self.settings.value(key, default)
        # Konversi tipe jika diperlukan, QSettings bisa mengembalikan tipe yang salah kadang-kadang
        if type is bool and not isinstance(value, bool):
            value = str(value).lower() in ('true', '1', 't', 'y', 'yes')
        elif type is float and not isinstance(value, float):
            try:
                value = float(value)
            except ValueError:
                logger.warning(f"Gagal mengkonversi nilai pengaturan '{key}' ke float: {value}. Menggunakan default: {default}")
                value = default
        elif type is int and not isinstance(value, int):
            try:
                value = int(value)
            except ValueError:
                logger.warning(f"Gagal mengkonversi nilai pengaturan '{key}' ke int: {value}. Menggunakan default: {default}")
                value = default
        logger.debug(f"Pengaturan dibaca: {key} = {value} (default: {default})")
        return value
        
    def check_file(self, file_path: str) -> CheckResult:
        """Check a single file for compliance with formatting rules"""
        logger.info(f"Mulai memeriksa file: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"File tidak ditemukan: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        try:
            if file_ext == '.docx':
                result = self._check_docx_file(file_path, filename)
            elif file_ext == '.pdf':
                result = self._check_pdf_file(file_path, filename)
            else:
                result = CheckResult(
                    filename=filename,
                    success=False,
                    messages=["Format file tidak didukung. Hanya file .docx atau .pdf yang dapat diperiksa."]
                )
        except Exception as e:
            result = CheckResult(
                filename=filename,
                success=False,
                messages=[f"Error saat memeriksa file: {str(e)}"]
            )
            logger.exception(f"Error saat memeriksa file {filename}") # Mencatat traceback juga
            
        # Emit signal for the completed check
        self.check_completed.emit(result)
        return result
        
    def _check_docx_file(self, file_path: str, filename: str) -> CheckResult:
        """Load and check a DOCX file"""
        logger.debug(f"Memeriksa file DOCX: {filename}")
        try:
            with open(file_path, 'rb') as f:
                doc = Document(f)
            return self._check_docx(doc, filename)
        except Exception as e:
            logger.exception(f"Gagal memproses file DOCX {filename}")
            raise Exception(f"Failed to process DOCX file: {str(e)}")
    
    def _check_pdf_file(self, file_path: str, filename: str) -> CheckResult:
        """Load and check a PDF file"""
        logger.debug(f"Memeriksa file PDF: {filename}")
        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            file_stream = io.BytesIO(file_bytes)
            return self._check_pdf(file_stream, filename)
        except Exception as e:
            logger.exception(f"Gagal memproses file PDF {filename}")
            raise Exception(f"Failed to process PDF file: {str(e)}")
    
    def _check_docx(self, doc: Document, filename: str) -> CheckResult:
        """Check DOCX file for compliance with formatting rules"""
        report = []
        success = True
        details = {
            "font_issues": [],
            "size_issues": [],
            "spacing_issues": [],
            "margin_issues": []
        }

        # Load settings for rules
        expected_font_name = self._get_setting("font_name", "Times New Roman")
        expected_font_size = self._get_setting("font_size", 12.0, type=float)
        expected_line_spacing = self._get_setting("line_spacing", 1.5, type=float)
        
        expected_margin_left = self._get_setting("margin_left", 4.0, type=float)
        expected_margin_right = self._get_setting("margin_right", 3.0, type=float)
        expected_margin_top = self._get_setting("margin_top", 3.0, type=float)
        expected_margin_bottom = self._get_setting("margin_bottom", 3.0, type=float)
        margin_tolerance = self._get_setting("margin_tolerance", 0.1, type=float)

        # Check font, size, and spacing
        for para_idx, para in enumerate(doc.paragraphs):
            # Skip empty paragraphs
            if not para.text.strip():
                continue
                
            # Check font and size
            for run in para.runs:
                # Skip empty runs
                if not run.text.strip():
                    continue
                    
                # Determine the effective font name
                effective_font_name = run.font.name
                if effective_font_name is None:
                    if run.style and run.style.font:
                        effective_font_name = run.style.font.name
                if effective_font_name is None:
                    if para.style and para.style.font:
                        effective_font_name = para.style.font.name
                
                # Use "Default" if still None after checking styles
                display_font_name = effective_font_name or "Default"

                if effective_font_name != expected_font_name:
                    # Allow for cases where Times New Roman might be a part of the name (e.g. "Times New Roman PSMT")
                    # However, for strict checking, we might want to remove this leniency.
                    # For now, let's assume the user wants an exact match or clearly inherited.
                    is_expected_font = False
                    if effective_font_name: # Check if not None
                        if expected_font_name.lower() in effective_font_name.lower():
                             is_expected_font = True
                    
                    if not is_expected_font:
                        msg = f'Font tidak sesuai di paragraf: "{para.text[:30]}..."'
                        report.append(msg)
                        details["font_issues"].append({
                            "paragraph": para_idx,
                            "text": para.text[:50],
                            "found": display_font_name,
                            "expected": expected_font_name
                        })
                        success = False
                        logger.debug(f"[DOCX] Font tidak sesuai: Para {para_idx+1}, Ditemukan='{display_font_name}', Diharapkan='{expected_font_name}', Teks='{para.text[:30]}...'")
                        # We break here because one run with wrong font makes the paragraph fail font check.
                        # If you want to report all non-compliant runs in a paragraph, remove this break.
                        break
                    
                # Check font size (using effective_font_name to ensure we are checking the size of the correct font)
                # Note: python-docx primarily gives direct formatting for size. 
                # Inherited size is harder to get accurately without deep style traversal.
                # We'll stick to run.font.size for now, as it's the most common case.
                if run.font.size and run.font.size.pt != expected_font_size:
                    msg = f'Ukuran font tidak sesuai di paragraf: "{para.text[:30]}..."'
                    report.append(msg)
                    details["size_issues"].append({
                        "paragraph": para_idx,
                        "text": para.text[:50],
                        "found": run.font.size.pt,
                        "expected": expected_font_size
                    })
                    success = False
                    logger.debug(f"[DOCX] Ukuran font tidak sesuai: Para {para_idx+1}, Ditemukan='{run.font.size.pt}', Diharapkan='{expected_font_size}', Teks='{para.text[:30]}...'")
                    break

            # Check spacing
            if para.paragraph_format.line_spacing is not None:
                spacing = para.paragraph_format.line_spacing
                if spacing != expected_line_spacing:
                    msg = f'Spasi tidak sesuai di paragraf: "{para.text[:30]}..."'
                    report.append(msg)
                    details["spacing_issues"].append({
                        "paragraph": para_idx,
                        "text": para.text[:50],
                        "found": spacing,
                        "expected": expected_line_spacing
                    })
                    success = False
                    logger.debug(f"[DOCX] Spasi tidak sesuai: Para {para_idx+1}, Ditemukan='{spacing}', Diharapkan='{expected_line_spacing}', Teks='{para.text[:30]}...'")

        # Check margins in cm
        sections = doc.sections
        if sections:
            section = sections[0]
            # Convert inches to cm (1 inch = 2.54 cm)
            left_margin_cm = section.left_margin.inches * 2.54
            right_margin_cm = section.right_margin.inches * 2.54
            top_margin_cm = section.top_margin.inches * 2.54
            bottom_margin_cm = section.bottom_margin.inches * 2.54

            # Expected margins
            expected_margins_cm = {
                'left': expected_margin_left,
                'right': expected_margin_right,
                'top': expected_margin_top,
                'bottom': expected_margin_bottom
            }

            tolerance = margin_tolerance

            if abs(left_margin_cm - expected_margins_cm['left']) > tolerance:
                msg = f'Margin kiri tidak sesuai: {left_margin_cm:.2f} cm (Diharapkan: {expected_margins_cm["left"]} cm)'
                report.append(msg)
                details["margin_issues"].append({
                    "margin": "left",
                    "found": left_margin_cm,
                    "expected": expected_margins_cm["left"]
                })
                success = False
                logger.debug(f"[DOCX] Margin kiri tidak sesuai: Ditemukan={left_margin_cm:.2f}cm, Diharapkan={expected_margins_cm['left']:.2f}cm")
                
            if abs(right_margin_cm - expected_margins_cm['right']) > tolerance:
                msg = f'Margin kanan tidak sesuai: {right_margin_cm:.2f} cm (Diharapkan: {expected_margins_cm["right"]} cm)'
                report.append(msg)
                details["margin_issues"].append({
                    "margin": "right",
                    "found": right_margin_cm,
                    "expected": expected_margins_cm["right"]
                })
                success = False
                logger.debug(f"[DOCX] Margin kanan tidak sesuai: Ditemukan={right_margin_cm:.2f}cm, Diharapkan={expected_margins_cm['right']:.2f}cm")
                
            if abs(top_margin_cm - expected_margins_cm['top']) > tolerance:
                msg = f'Margin atas tidak sesuai: {top_margin_cm:.2f} cm (Diharapkan: {expected_margins_cm["top"]} cm)'
                report.append(msg)
                details["margin_issues"].append({
                    "margin": "top",
                    "found": top_margin_cm,
                    "expected": expected_margins_cm["top"]
                })
                success = False
                logger.debug(f"[DOCX] Margin atas tidak sesuai: Ditemukan={top_margin_cm:.2f}cm, Diharapkan={expected_margins_cm['top']:.2f}cm")
                
            if abs(bottom_margin_cm - expected_margins_cm['bottom']) > tolerance:
                msg = f'Margin bawah tidak sesuai: {bottom_margin_cm:.2f} cm (Diharapkan: {expected_margins_cm["bottom"]} cm)'
                report.append(msg)
                details["margin_issues"].append({
                    "margin": "bottom",
                    "found": bottom_margin_cm,
                    "expected": expected_margins_cm["bottom"]
                })
                success = False
                logger.debug(f"[DOCX] Margin bawah tidak sesuai: Ditemukan={bottom_margin_cm:.2f}cm, Diharapkan={expected_margins_cm['bottom']:.2f}cm")
        else:
            report.append('Tidak dapat memeriksa margin.')
            logger.warning("[DOCX] Tidak ada section ditemukan, tidak dapat memeriksa margin.")
            success = False

        logger.info(f"Pemeriksaan DOCX selesai untuk {filename}. Sukses: {success}, Pesan: {len(report)} isu.")
        return CheckResult(filename=filename, success=success, messages=report, details=details)

    def _check_pdf(self, file_stream: io.BytesIO, filename: str) -> CheckResult:
        """Check PDF file for compliance with formatting rules"""
        report = []
        success = True
        details = {
            "font_issues": [],
            "size_issues": []
        }
        
        # Load settings for rules
        expected_font_name = self._get_setting("font_name", "Times New Roman")
        expected_font_size = self._get_setting("font_size", 12.0, type=float)
        # PDF line spacing check is more complex and might need specific library features.
        # For now, we'll focus on font and size for PDF.
        
        try:
            doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        except Exception as e:
            logger.exception(f"Gagal membaca PDF {filename}")
            return CheckResult(
                filename=filename,
                success=False, 
                messages=[f'Gagal membaca dokumen PDF: {str(e)}']
            )

        # Check font and font size
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get('type', -1) != 0:  # Text only
                    continue
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        font_name = span.get('font', 'Unknown')
                        font_size = span.get('size', 0)
                        text = span.get('text', '')

                        # Check font name (allow partial match for robustness)
                        if expected_font_name.lower() not in font_name.lower():
                            msg = f'Font tidak sesuai di halaman {page_num + 1}: "{text[:30]}..." (Ditemukan: {font_name})'
                            if msg not in report: # Avoid duplicate messages for the same page/font
                                report.append(msg)
                                details["font_issues"].append({
                                    "page": page_num + 1,
                                    "text": text[:50],
                                    "found": font_name,
                                    "expected": expected_font_name
                                })
                                success = False
                                logger.debug(f"[PDF] Font tidak sesuai: Hal {page_num+1}, Ditemukan='{font_name}', Diharapkan='{expected_font_name}', Teks='{text[:30]}...'")
                        
                        # Check font size
                        if abs(font_size - expected_font_size) > 0.5: # Tolerance for PDF font size
                            msg = f'Ukuran font tidak sesuai di halaman {page_num + 1}: "{text[:30]}..." (Ditemukan: {font_size:.1f}pt)'
                            if msg not in report: # Avoid duplicate messages
                                report.append(msg)
                                details["size_issues"].append({
                                    "page": page_num + 1,
                                    "text": text[:50],
                                    "found": f"{font_size:.1f}pt",
                                    "expected": f"{expected_font_size:.1f}pt"
                                })
                                success = False
                                logger.debug(f"[PDF] Ukuran font tidak sesuai: Hal {page_num+1}, Ditemukan='{font_size:.1f}pt', Diharapkan='{expected_font_size:.1f}pt', Teks='{text[:30]}...'")

        # Note about margin checking
        report.append('Pemeriksaan margin pada PDF tidak dilakukan secara mendalam.')

        logger.info(f"Pemeriksaan PDF selesai untuk {filename}. Sukses: {success}, Pesan: {len(report)} isu.")
        return CheckResult(filename=filename, success=success, messages=report, details=details) 