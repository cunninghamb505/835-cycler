# RemitView

EDI X12 835 Remittance Analyzer — parse, view, and analyze healthcare remittance data.

**Author:** Brandon Cunningham
**Version:** 2.1.0

## What It Does

Healthcare providers receive 835 remittance files from insurance payers to explain how claims were processed — what was paid, denied, or adjusted, and why. These files are raw EDI, a dense format that's difficult to read without specialized software.

RemitView parses these files and presents the data in a clean web interface. Upload an 835 file (or load the built-in samples) and instantly see payment totals, individual claim breakdowns, service-line details, and adjustment reason codes. Filter claims by status, payer, or date range. Look up any CARC, RARC, or claim status code to understand why a claim was adjusted.

## Features

### Core
- **File Upload** — Parse EDI X12 835 (.835, .edi, .txt, .x12) and PDF remittance files
- **Dashboard** — Payment totals, claim counts, and adjustment breakdowns at a glance
- **Claims Browser** — Filter and search claims by status, payer, date range
- **Claim Detail** — Service lines, adjustments, provider info, and flagging for each claim
- **Code Lookup** — Search CARC/RARC/claim status codes with descriptions
- **Global Search** — Search across claims, patients, and procedure codes

### Analytics
- **Denial Trends** — Line charts showing denial patterns over time by payer, reason, or provider
- **Payer Comparison** — Bar charts comparing payment rates and top denial reasons across payers
- **Adjustment Summary** — Doughnut chart and detail table for adjustment group/reason codes

### Workflow
- **Claim Flagging** — Flag claims for review with notes, resolve when addressed
- **Underpayment Detection** — Configurable threshold to highlight potentially underpaid claims
- **Multi-File Compare** — Side-by-side comparison showing added, removed, and changed claims

### Export & Reporting
- **CSV Export** — Export claim data for spreadsheets
- **Excel Export** — Multi-sheet workbook with summary, claims, service lines, and adjustments
- **PDF Reports** — Professional PDF reports for individual claims or full files

### Data Integration
- **PDF Remittance Parsing** — Parse PDF remittance advice documents from common payers
- **837 Claim Matching** — Upload 837 claim files to compare expected vs actual payments
- **File Watcher** — Monitor a folder for new EDI files and auto-import them

### Listeners
- **FTP Server** — Embedded FTP server for receiving EDI files from external systems
- **Email/IMAP Listener** — Polls an email inbox for EDI/PDF attachments and auto-imports
- **Webhook Endpoint** — HTTP POST endpoint with API key authentication for programmatic ingest

### Developer Tools
- **Raw File Viewer** — Inspect the raw EDI content of any imported file
- **File Editor** — Edit raw EDI content and re-parse to update all associated data
- **API Key Management** — Create and manage API keys for webhook/external access

### UX
- **Dark/Light Theme** — Toggle between themes
- **Keyboard Shortcuts** — Navigate pages (1-9), search (/), help (?), and more
- **Responsive Layout** — Works on desktop and tablet

## Screenshots

![Load File](image-2.png)
![Dashboard](image.png)
![Claims](image-1.png)

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000)

### Local

Requires Python 3.13+

```bash
pip install -r requirements.txt
python run.py
```

Open [http://localhost:8000](http://localhost:8000)

### Windows Executable

Build a standalone .exe with system tray icon:

```bash
pip install -r requirements-build.txt
python build_windows.py
```

The executable will be in `dist/RemitView.exe`.

## Tech Stack

- **Backend** — Python 3.13, FastAPI, SQLite (WAL mode)
- **Frontend** — Vanilla HTML/CSS/JS (no frameworks)
- **Parser** — Custom state-machine EDI X12 835 parser
- **Charts** — Chart.js 4.x (bundled locally)
- **Export** — openpyxl (Excel), reportlab (PDF)
- **Listeners** — pyftpdlib (FTP), imaplib (Email), FastAPI (Webhook)

## API

RemitView exposes 48 REST API endpoints. Full docs available at `/docs` when the server is running.

Key endpoints:
- `POST /api/files/upload` — Upload and parse an 835 file
- `GET /api/claims` — List claims with filters
- `GET /api/dashboard` — Dashboard summary stats
- `POST /api/ingest` — Webhook file ingest (API key required)
- `GET /api/listeners/status` — Listener status
- `GET /api/developer/files/{id}/raw` — Raw file content

## License

MIT
