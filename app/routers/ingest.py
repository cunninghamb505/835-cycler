"""Webhook ingest endpoint — accepts files from external systems via HTTP POST."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.services import file_service
from app.parser.pdf_parser import parse_pdf_remittance
from app.auth import verify_api_key
from app.config import settings

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("")
async def ingest_file(request: Request, file: UploadFile = File(...)):
    """Ingest a file from an external system.

    Requires a valid API key via Authorization: Bearer <key> header.
    Accepts .835, .edi, .txt, .x12, and .pdf files.
    """
    # Verify API key
    key_info = verify_api_key(request)
    if not key_info:
        raise HTTPException(status_code=401, detail="API key required. Use Authorization: Bearer <key>")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    filename = file.filename.lower()
    source_name = key_info.get("key_name", "webhook")

    # PDF remittance
    if filename.endswith(".pdf"):
        try:
            parsed = parse_pdf_remittance(content)
            file_id = file_service.parse_and_store_parsed(
                parsed, f"[{source_name}] {file.filename}",
                source_type="pdf",
                pdf_notes=parsed.get("pdf_parsing_notes", ""),
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF parse error: {str(e)}")
        return {"status": "ok", "message": "PDF ingested", "file_id": file_id}

    # EDI file
    raw = content.decode("utf-8", errors="replace")
    if "ISA" not in raw[:100]:
        raise HTTPException(status_code=400, detail="Not a valid EDI X12 file (no ISA header)")

    try:
        file_id = file_service.parse_and_store(raw, f"[{source_name}] {file.filename}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")

    return {"status": "ok", "message": "File ingested", "file_id": file_id}


@router.post("/raw")
async def ingest_raw(request: Request):
    """Ingest raw EDI content in the request body.

    Requires API key. Send raw 835 content as the request body with
    Content-Type: text/plain.
    """
    key_info = verify_api_key(request)
    if not key_info:
        raise HTTPException(status_code=401, detail="API key required")

    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty body")

    raw = body.decode("utf-8", errors="replace")
    if "ISA" not in raw[:100]:
        raise HTTPException(status_code=400, detail="Not valid EDI X12 content")

    source_name = key_info.get("key_name", "webhook")
    try:
        file_id = file_service.parse_and_store(raw, f"[{source_name}] webhook_ingest.edi")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")

    return {"status": "ok", "message": "Raw EDI ingested", "file_id": file_id}
