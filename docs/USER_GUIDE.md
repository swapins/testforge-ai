# MVP user guide

## Start locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:TESTFORGE_DB_PATH = "testforge.sqlite3"
uvicorn app.main:app --reload
```

Bootstrap once with passwords supplied only in the local request:

```powershell
curl.exe -X POST http://127.0.0.1:8000/v1/auth/bootstrap -H "Content-Type: application/json" -d '{"developer_password":"local-developer-password","reviewer_password":"local-reviewer-password"}'
```

Sign in as `saritha` to create projects, generate and submit scenarios. Sign in
as `swapin` to approve or reject submitted cases. Only approved cases can be
exported; unsupported scenarios return `unsupported` instead of unsafe code.

The dashboard is available through `npm install; npm run dev` in `frontend`, or
through Docker Compose. The API remains the source of truth for authorization.
