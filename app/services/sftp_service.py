"""Embedded FTP server for receiving ERA files from external systems."""
import os
import logging
import threading
from pathlib import Path
from app.services import file_service
from app.services.settings_service import get_setting

logger = logging.getLogger(__name__)

_server = None
_thread = None


def _get_ftp_dir() -> Path:
    """Get or create the FTP upload directory."""
    custom = get_setting("sftp_directory")
    if custom and os.path.isdir(custom):
        return Path(custom)
    ftp_dir = Path.home() / "RemitView" / "ftp_incoming"
    ftp_dir.mkdir(parents=True, exist_ok=True)
    return ftp_dir


class AutoParseHandler:
    """Custom FTP handler that auto-parses uploaded files."""

    VALID_EXTENSIONS = {".edi", ".835", ".txt", ".x12"}

    @staticmethod
    def on_file_received(filepath: str):
        """Called after a file is fully uploaded via FTP."""
        ext = Path(filepath).suffix.lower()
        if ext not in AutoParseHandler.VALID_EXTENSIONS:
            logger.info(f"FTP: skipping non-EDI file {filepath}")
            return

        logger.info(f"FTP: auto-parsing {filepath}")
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                raw = f.read()
            if "ISA" not in raw[:100]:
                logger.warning(f"FTP: {filepath} has no ISA header, skipping")
                return
            filename = f"[FTP] {os.path.basename(filepath)}"
            file_id = file_service.parse_and_store(raw, filename)
            logger.info(f"FTP: imported {filepath} as file ID {file_id}")
        except Exception as e:
            logger.error(f"FTP: error parsing {filepath}: {e}")


def start_ftp_server():
    """Start the embedded FTP server."""
    global _server, _thread

    try:
        from pyftpdlib.authorizers import DummyAuthorizer
        from pyftpdlib.handlers import FTPHandler
        from pyftpdlib.servers import FTPServer
    except ImportError:
        logger.warning("pyftpdlib not installed, FTP server disabled")
        return False

    port_str = get_setting("sftp_port") or "2121"
    username = get_setting("sftp_username") or "remitview"
    password = get_setting("sftp_password") or "remitview"

    try:
        port = int(port_str)
    except ValueError:
        port = 2121

    ftp_dir = _get_ftp_dir()

    stop_ftp_server()

    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, str(ftp_dir), perm="elradfmw")

    class ParseOnUploadHandler(FTPHandler):
        def on_file_received(self, filepath):
            AutoParseHandler.on_file_received(filepath)

    ParseOnUploadHandler.authorizer = authorizer
    ParseOnUploadHandler.passive_ports = range(60000, 60100)
    ParseOnUploadHandler.banner = "RemitView FTP Server"

    try:
        _server = FTPServer(("0.0.0.0", port), ParseOnUploadHandler)
        _server.max_cons = 10
        _server.max_cons_per_ip = 3

        _thread = threading.Thread(target=_server.serve_forever, daemon=True)
        _thread.start()
        logger.info(f"FTP server started on port {port}, directory: {ftp_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to start FTP server: {e}")
        _server = None
        return False


def stop_ftp_server():
    """Stop the FTP server if running."""
    global _server, _thread
    if _server:
        try:
            _server.close_all()
        except Exception:
            pass
        _server = None
        _thread = None
        logger.info("FTP server stopped")


def is_running() -> bool:
    """Check if the FTP server is currently running."""
    return _server is not None and _thread is not None and _thread.is_alive()


def get_status() -> dict:
    """Get FTP server status."""
    port = get_setting("sftp_port") or "2121"
    return {
        "running": is_running(),
        "port": port,
        "directory": str(_get_ftp_dir()),
        "username": get_setting("sftp_username") or "remitview",
    }
