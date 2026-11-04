# Deployment

## Docker Compose

```powershell
docker compose up --build
```

The API is at `http://localhost:8000`; the development dashboard is at
`http://localhost:5173`. The Compose configuration uses a named SQLite volume
and keeps execution disabled.

For a local synthetic execution demonstration only, set
`TESTFORGE_ENABLE_EXECUTION=1` for the API and ensure Java 17, Maven, and Chrome
are available in the execution environment. Do not expose this mode to the
public internet. The execution path is intentionally not a general-purpose
command runner.

GitHub Actions runs Python tests, Java/Selenium tests with the setup action's
matching browser binary, and the frontend production build.
