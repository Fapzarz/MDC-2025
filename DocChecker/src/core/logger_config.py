import logging
import os
from PySide6.QtCore import QSettings, QStandardPaths

def setup_logging(settings: QSettings):
    """Konfigurasi logging berdasarkan pengaturan."""
    log_enabled = settings.value("developer/extensive_logging", False, type=bool)
    
    # Hapus handler yang ada untuk menghindari duplikasi jika fungsi ini dipanggil beberapa kali
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    if log_enabled:
        log_level = logging.DEBUG
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        
        # Tentukan path untuk file log di direktori data aplikasi
        log_dir = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "mdc2025_debug.log")

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file_path, mode='a', encoding='utf-8'), # Menyimpan ke file
                logging.StreamHandler()  # Juga output ke konsol
            ]
        )
        logging.info(f"Logging ekstensif diaktifkan. Log disimpan di: {log_file_path}")
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Logging ekstensif dinonaktifkan. Hanya warning dan error yang akan dicatat.") 