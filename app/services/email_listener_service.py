"""Email/IMAP listener for auto-importing ERA file attachments."""
import imaplib
import email
import logging
import threading
import time
from email.header import decode_header
from pathlib import Path
from app.services import file_service
from app.services.settings_service import get_setting
from app.parser.pdf_parser import parse_pdf_remittance

logger = logging.getLogger(__name__)

_running = False
_thread = None

VALID_EXTENSIONS = {".edi", ".835", ".txt", ".x12", ".pdf"}


def _check_inbox():
    """Connect to IMAP and process new emails with EDI/PDF attachments."""
    host = get_setting("email_imap_host")
    port_str = get_setting("email_imap_port") or "993"
    username = get_setting("email_username")
    password = get_setting("email_password")
    folder = get_setting("email_folder") or "INBOX"
    use_ssl = (get_setting("email_use_ssl") or "true").lower() == "true"

    if not host or not username or not password:
        return 0

    try:
        port = int(port_str)
    except ValueError:
        port = 993

    processed = 0

    try:
        if use_ssl:
            mail = imaplib.IMAP4_SSL(host, port)
        else:
            mail = imaplib.IMAP4(host, port)

        mail.login(username, password)
        mail.select(folder)

        # Search for unseen emails
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            return 0

        for msg_num in messages[0].split():
            if not msg_num:
                continue

            status, msg_data = mail.fetch(msg_num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subject = ""
            raw_subject = decode_header(msg["Subject"] or "")
            for part, encoding in raw_subject:
                if isinstance(part, bytes):
                    subject += part.decode(encoding or "utf-8", errors="replace")
                else:
                    subject += part

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue

                filename = part.get_filename()
                if not filename:
                    continue

                ext = Path(filename).suffix.lower()
                if ext not in VALID_EXTENSIONS:
                    continue

                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                logger.info(f"Email: processing attachment {filename} from '{subject}'")
                tagged_name = f"[Email] {filename}"

                try:
                    if ext == ".pdf":
                        parsed = parse_pdf_remittance(payload)
                        file_service.parse_and_store_parsed(
                            parsed, tagged_name,
                            source_type="pdf",
                            pdf_notes=parsed.get("pdf_parsing_notes", ""),
                        )
                    else:
                        raw = payload.decode("utf-8", errors="replace")
                        if "ISA" in raw[:100]:
                            file_service.parse_and_store(raw, tagged_name)
                        else:
                            logger.warning(f"Email: {filename} has no ISA header, skipping")
                            continue

                    processed += 1
                    logger.info(f"Email: imported {filename}")
                except Exception as e:
                    logger.error(f"Email: error processing {filename}: {e}")

        mail.logout()
    except Exception as e:
        logger.error(f"Email listener error: {e}")

    return processed


def _poll_loop():
    """Background polling loop."""
    global _running

    interval_str = get_setting("email_poll_interval") or "300"
    try:
        interval = int(interval_str)
    except ValueError:
        interval = 300

    while _running:
        try:
            count = _check_inbox()
            if count > 0:
                logger.info(f"Email: imported {count} file(s)")
        except Exception as e:
            logger.error(f"Email poll error: {e}")

        # Sleep in small increments so we can stop quickly
        for _ in range(interval):
            if not _running:
                break
            time.sleep(1)


def start_listener():
    """Start the email listener background thread."""
    global _running, _thread

    host = get_setting("email_imap_host")
    username = get_setting("email_username")
    password = get_setting("email_password")

    if not host or not username or not password:
        logger.info("Email listener not configured, skipping")
        return False

    stop_listener()

    _running = True
    _thread = threading.Thread(target=_poll_loop, daemon=True)
    _thread.start()
    logger.info("Email listener started")
    return True


def stop_listener():
    """Stop the email listener."""
    global _running, _thread
    _running = False
    if _thread:
        _thread.join(timeout=5)
        _thread = None
    logger.info("Email listener stopped")


def is_running() -> bool:
    """Check if the email listener is running."""
    return _running and _thread is not None and _thread.is_alive()


def get_status() -> dict:
    """Get email listener status."""
    return {
        "running": is_running(),
        "host": get_setting("email_imap_host") or "",
        "username": get_setting("email_username") or "",
        "folder": get_setting("email_folder") or "INBOX",
        "poll_interval": get_setting("email_poll_interval") or "300",
        "configured": bool(get_setting("email_imap_host") and get_setting("email_username")),
    }
