# Local Development Setup Guide (Windows PowerShell)

This guide provides exact, reproducible steps to configure the development environment on Windows 11.

---

## 1. Prerequisites Check

Open PowerShell and verify the installed tools:

```powershell
# Check Git
git --version

# Check Node.js and npm
node --version
npm --version

# Check PostgreSQL service
Get-Service -Name postgresql-x64-17

# Check available Python versions via Python Launcher
py -0p
```

### Expected Versions
* **Git:** 2.40+ (Installed)
* **Node.js:** v20+ or v22+ (Installed: v22.11.0)
* **npm:** 10+ (Installed: 10.9.0)
* **PostgreSQL:** 16+ or 17+ (Installed: PostgreSQL 17.5 service running)
* **Python:** Python 3.11 is required for project virtual environment.

---

## 2. Python 3.11 Installation (If Not Present)

If `py -0p` shows only Python 3.13, install Python 3.11:

### Option A: Via Windows Package Manager (`winget`) (Recommended)
```powershell
winget install --id Python.Python.3.11 --exact --source winget
```

### Option B: Via Official Python Installer
1. Download Python 3.11.9 (64-bit) installer from [python.org](https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe).
2. During installation, ensure **"Add python.exe to PATH"** and **"Install launcher for all users (py.exe)"** are checked.

After installation, verify Python 3.11 is recognized:
```powershell
py -3.11 --version
```
Expected output: `Python 3.11.x`

---

## 3. Python Virtual Environment Setup

From the repository root (`DocumentAI-Thesis-`):

### Step 3.1: Create Project Virtual Environment
```powershell
py -3.11 -m venv .venv
```

### Step 3.2: Configure PowerShell Execution Policy (If Script Execution Is Disabled)
If PowerShell blocks script execution, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Step 3.3: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```
*(Your terminal prompt should now show `(.venv)`).*

### Step 3.4: Verify Python Version Inside Virtual Environment
```powershell
python --version
```
Expected output: `Python 3.11.x` (ensures `.venv` uses 3.11, not global 3.13).

---

## 4. Install Backend Dependencies

With `(.venv)` activated:

```powershell
# Upgrade pip, setuptools, and wheel
python -m pip install --upgrade pip setuptools wheel

# Install minimal backend dependencies
pip install -r backend/requirements-dev.txt
```

---

## 5. Environment Configuration

Copy the example configuration file:

```powershell
Copy-Item .env.example .env
```

Open `.env` in your editor and configure your local PostgreSQL credentials:
```ini
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_actual_postgres_password
DB_NAME=documentai_thesis
TEST_DB_NAME=documentai_thesis_test
```

### 5.1 Database Initialization & Alembic Migrations

From repository root with `(.venv)` activated:

```powershell
# 1. Create development and isolated test databases (run once)
psql -h localhost -U postgres -c "CREATE DATABASE documentai_thesis;"
psql -h localhost -U postgres -c "CREATE DATABASE documentai_thesis_test;"

# 2. Apply Alembic migrations to development database
alembic -c backend/alembic.ini upgrade head

# 3. Check migration status
alembic -c backend/alembic.ini current
```

---

## 6. Verify Development Server & Tests

With `(.venv)` activated:

### Run the Full Test Suite
Executes both SQLite in-memory unit tests and real PostgreSQL integration tests:
```powershell
pytest
```

### Run Unit Tests Only (SQLite In-Memory)
```powershell
pytest backend/tests/test_models.py
```

### Run PostgreSQL Integration Tests Only (Isolated Test DB)
```powershell
pytest backend/tests/test_postgres_integration.py
```

### Start FastAPI Development Server
```powershell
uvicorn app.main:app --app-dir backend --reload --port 8000
```
Open your browser to:
* Health check: `http://127.0.0.1:8000/health`
* Interactive API Documentation: `http://127.0.0.1:8000/docs`

---

## 7. Deactivating the Virtual Environment

When finished working:
```powershell
deactivate
```

---

## 8. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy restricted | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in current session. |
| `py : No suitable Python runtime found` | Python 3.11 not installed | Install Python 3.11 using `winget install --id Python.Python.3.11`. |
| `psql: error: connection to server on socket failed` | PostgreSQL service stopped | Run `Start-Service postgresql-x64-17` in an administrative terminal or check Windows Services. |
| Port 8000 already in use | Another process running on port 8000 | Use `--port 8001` or terminate the lingering process. |
