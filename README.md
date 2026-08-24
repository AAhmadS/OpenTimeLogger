<div align="center">

# OpenTimeLogger

**A glass-morphism desktop time tracker that keeps every session on your disk — and exports it to Excel.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg)
![Built with pywebview](https://img.shields.io/badge/built%20with-pywebview-0B3B8C.svg)

</div>

---

OpenTimeLogger is a small, private-by-design desktop app for logging what you work on. Start and stop sessions with a click — or backfill when they *actually* started and ended — and let it silently measure how long you spend writing each session's notes. Everything lives in one readable `sessions.json`, and one click turns any date range into a filtered Excel workbook.

No accounts. No cloud. No telemetry. Your time is your file.

---

## Screenshots

<div align="center">

| Start a session | Edit an archived session | Export to Excel |
|:---:|:---:|:---:|
| ![Start a session](screenshots/start.png) | ![Edit an archived session](screenshots/archive-edit.png) | ![Export to Excel](screenshots/export.png) |

</div>

---

## Features

- **Start & end, now or at a time** — begin right away, or tell it the moment a session *actually* started and finished.
- **Overlapping sessions** — run several sessions in parallel; each is tracked independently.
- **Active / Archive side menu** — running sessions on one side, finished ones in the archive. Archive entries are fully editable: times, category, tag, sub-tag, description, notes — and can be reopened into Active.
- **`category: tag + sub-tag` naming** — sessions are named `Category: tag + sub-tag`. Category, tag and description are essential; sub-tag and notes are optional. You can also name a session up front when you start it.
- **Automatic documentation tracking** — the app measures the time you spend writing a session's documentation and logs it on the session. At the end of each day it sums documentation time **per category** into a single `documentation`-tagged summary record, so you can see exactly how much time went into writing things up.
- **Excel export** — filter finished sessions by category, tag and date range (Today → All time) and export a styled `.xlsx`. When a single category is selected, the Category column is dropped automatically.
- **Private by design** — a single `sessions.json` next to the app; close the window and the process exits. Nothing leaves your machine.

## Getting started

### Option A — run the prebuilt app

Grab `OpenTimeLogger.exe` from the [Releases](../../releases) page and double-click it. No Python required.

> Requires the WebView2 runtime, which ships with Windows 10 and Windows 11.

### Option B — run from source

Requires Python 3.11+ on Windows.

```bash
git clone https://github.com/AAhmadS/OpenTimeLogger.git
cd OpenTimeLogger
pip install -r requirements.txt
pythonw session_logger.py     # or: python session_logger.py
```

### Building the standalone `.exe`

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed \
  --name OpenTimeLogger --icon app.ico \
  --hidden-import webview.platforms.winforms \
  session_logger.py
```

The binary lands in `dist/OpenTimeLogger.exe`.

## How it stores data

| File | Purpose |
| --- | --- |
| `sessions.json` | Every session and the daily documentation summaries. Created next to the app on first run. |
| `exports/*.xlsx` | Excel workbooks produced by the export feature. |

`sessions.json` is plain JSON — readable, editable, and easy to back up or migrate. Old-format files from earlier versions are migrated automatically on first launch.

## Project structure

```
OpenTimeLogger/
├── session_logger.py    # backend: JSON store, session logic, Excel export, webview host
├── ui.py                # the entire glass UI (HTML/CSS/JS) embedded as a string
├── brand.py             # generated avatar, embedded as a data URI
├── app.ico              # application icon
├── assets/              # generated icon & avatar sources
├── requirements.txt
└── screenshots/         # this README's screenshots
```

## Contributing

OpenTimeLogger is a tiny, focused project — good first contributions:

- Linux/macOS support (the UI is platform-neutral; only the webview host and build are Windows-tuned)
- A CSV export option
- iCal / calendar feeds from archived sessions
- Weekly roll-up reports (monthly, weekly views)

Open an issue before a large change so we can agree on direction.

## License

[MIT](LICENSE) © 2026 Amirahmad Shafiee

## Credits

- [pywebview](https://pywebview.flowrl.com) — native window + webview host
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel export
- [WaveSpeed](https://wavespeed.ai) / ByteDance Seedream 5-lite — generated icon & avatar
- [xiaomi/mimo-v2.5](https://openrouter.ai) — UI review of the rendered app