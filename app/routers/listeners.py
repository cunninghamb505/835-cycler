"""Listener management endpoints — FTP server, email poller, webhook info."""
from fastapi import APIRouter
from app.services import sftp_service, email_listener_service
from app.services.settings_service import get_setting, set_setting

router = APIRouter(prefix="/api/listeners", tags=["listeners"])


@router.get("/status")
async def get_all_status():
    """Get status of all listeners."""
    return {
        "ftp": sftp_service.get_status(),
        "email": email_listener_service.get_status(),
        "webhook": {
            "endpoint": "/api/ingest",
            "raw_endpoint": "/api/ingest/raw",
            "auth": "API key required (Authorization: Bearer <key>)",
        },
    }


@router.post("/ftp/start")
async def start_ftp():
    """Start the embedded FTP server."""
    ok = sftp_service.start_ftp_server()
    if not ok:
        return {"status": "error", "message": "Failed to start FTP server (pyftpdlib may not be installed)"}
    return {"status": "ok", "message": "FTP server started"}


@router.post("/ftp/stop")
async def stop_ftp():
    """Stop the FTP server."""
    sftp_service.stop_ftp_server()
    return {"status": "ok", "message": "FTP server stopped"}


@router.post("/email/start")
async def start_email():
    """Start the email/IMAP listener."""
    ok = email_listener_service.start_listener()
    if not ok:
        return {"status": "error", "message": "Email listener not configured (set IMAP host, username, password in settings)"}
    return {"status": "ok", "message": "Email listener started"}


@router.post("/email/stop")
async def stop_email():
    """Stop the email listener."""
    email_listener_service.stop_listener()
    return {"status": "ok", "message": "Email listener stopped"}


@router.post("/email/check")
async def check_email():
    """Manually check the email inbox now."""
    from app.services.email_listener_service import _check_inbox
    try:
        count = _check_inbox()
        return {"status": "ok", "message": f"Checked inbox, imported {count} file(s)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.put("/settings")
async def update_listener_settings(body: dict):
    """Update listener configuration settings."""
    allowed_keys = {
        "sftp_port", "sftp_username", "sftp_password", "sftp_directory",
        "email_imap_host", "email_imap_port", "email_username", "email_password",
        "email_folder", "email_use_ssl", "email_poll_interval",
    }
    updated = []
    for key, value in body.items():
        if key in allowed_keys:
            set_setting(key, value)
            updated.append(key)
    return {"status": "ok", "updated": updated}


@router.get("/settings")
async def get_listener_settings():
    """Get all listener configuration settings."""
    keys = [
        "sftp_port", "sftp_username", "sftp_password", "sftp_directory",
        "email_imap_host", "email_imap_port", "email_username", "email_password",
        "email_folder", "email_use_ssl", "email_poll_interval",
    ]
    result = {}
    for key in keys:
        result[key] = get_setting(key) or ""
    return result
