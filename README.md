# project_dsa_management_suite

## Data Structures & Algorithms Management Suite

A Python/Tkinter desktop application demonstrating search, sorting, scheduling, interval overlap, and core data structures through inventory, scheduling, and resource-management modules.

- Original location: `D:\Computers Files\work\uk work\algorithms___data_structure`
- Working copy: `D:\PROJECTS_READY\project_dsa_management_suite`
- GitHub: <https://github.com/rabin0811/project_dsa_management_suite>
- Stack: Python 3, customtkinter, Pillow, SQLite

## Folder layout

```text
project_dsa_management_suite/
  app/
    algorithms/     Search, sorting, scheduling, interval logic
    controllers/    MVC controllers
    models/         Domain models
    views/          Tkinter views
    utils/          Database, config, logging helpers
    data/           SQLite runtime database
    logs/           Runtime logs
  docs/             Project documentation
```

## Setup and run

```powershell
cd app
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Configuration is read from `app/config.json` and can be overridden with `app/.env`.

## Verified status (2026-11-09)

- [x] Python sources compiled
- [x] Modules imported successfully
- [x] Tkinter/customtkinter GUI launched successfully
- [ ] No automated test suite was executed

## Notes and limitations

- Desktop GUI only; requires a graphical session.
- Uses SQLite under `app/data/` for local state.
- Runtime logs and the database are ignored by Git.
- The suite is a coursework demonstration, not a production scheduling system.
- Renamed from `project_uk_algorithms_suite` to `project_dsa_management_suite` on 2026-11-10.

## Troubleshooting

- **`customtkinter` missing**: run `python -m pip install -r requirements.txt`.
- **GUI does not open**: run from a desktop session with Tk support.
- **Database errors**: ensure `app/data/` is writable; the app recreates the SQLite schema as needed.
- **Config not applied**: check `app/config.json` and `app/.env` for overrides.
