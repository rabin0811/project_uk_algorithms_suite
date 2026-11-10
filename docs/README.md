# Data Structures & Algorithms Management Suite — Technical Notes

## Overview

A Python desktop application that demonstrates search, sorting, scheduling, interval-overlap, and core data-structure concepts through inventory, scheduling, and resource-management screens.

Renamed from `project_uk_algorithms_suite` to `project_dsa_management_suite` on 2026-11-10. GitHub: <https://github.com/rabin0811/project_dsa_management_suite>.

## Architecture

```text
Tkinter/customtkinter views
  └─ Controllers
       ├─ Algorithms (search, sort, schedule, intervals)
       ├─ Models (inventory, bookings, resources)
       └─ SQLite data store
```

## Folder structure

```text
app/
  algorithms/     Search, sorting, scheduling, interval logic
  controllers/    MVC controllers
  models/         Domain models
  views/          Tkinter views
  utils/          Database, config, and logging helpers
  data/           Runtime SQLite database
  logs/           Runtime logs
  main.py         Application entry point
  config.json     Runtime configuration
```

## Setup and run

```powershell
cd app
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Configuration

The app reads `app/config.json`. Local overrides can be placed in `app/.env`.

## Verification evidence (2026-11-09)

| Check | Result |
|---|---|
| Python sources compile | Passed |
| Module imports | Passed |
| Tkinter/customtkinter GUI | Launched successfully |
| Automated tests | None |

## Documentation files

- `HOW_TO_OPERATE.txt` — step-by-step operation guide.
- `TECHNICAL_REPORT.txt` — plain-text technical report.
- `Technical_Report.docx` — formatted report.

## Limitations

- Desktop GUI only; a graphical session is required.
- The SQLite database and logs are runtime data and are ignored by Git.
- This is a coursework demonstration, not a production scheduling system.
- No automated test suite is included.
