# Playwright Python Automation Framework

An extensible pytest and Playwright framework for UI and API checks against public practice applications. The examples use SauceDemo for browser tests and JSONPlaceholder for read-only API validation.

## Project layout

```text
pages/                 Reusable page objects
tests/ui/               Browser tests
tests/api/              API tests
testdata/               JSON test data
models/                 API response models
utils/                  Logging, JSON, session storage, and email helpers
logs/                   automation.log and failure traces
screenshots/            Screenshots from failed UI tests
conftest.py             Shared fixtures and pytest hooks
pytest.ini              Test discovery and markers
requirements.txt        Python dependencies
.github/workflows/      CI workflow
```

## Setup

Use Python 3.10 or later. From this directory, create and activate a virtual environment, then install the dependencies and Chromium:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/playwright install chromium
```

On Linux CI, install browser system dependencies with `playwright install --with-deps chromium`.
On Windows, use `.venv\\Scripts\\python.exe` and `.venv\\Scripts\\playwright.exe` in place of `.venv/bin/...`.

## Run tests

```bash
# Full suite, including HTML report
.venv/bin/python -m pytest --html=reports/report.html --self-contained-html

# Smoke, regression, or read-only subsets
.venv/bin/python -m pytest -m smoke
.venv/bin/python -m pytest -m regression
.venv/bin/python -m pytest -m readonly
.venv/bin/python -m pytest -m "smoke or regression"

# Parallel execution
.venv/bin/python -m pytest -n 2

# Run UI tests against a different compatible practice site
APP_BASE_URL=https://www.saucedemo.com .venv/bin/python -m pytest tests/ui
```

If you prefer the shorter `pytest` command, first activate the environment with `source .venv/bin/activate` (Windows: `.venv\\Scripts\\activate`).

API tests use `API_BASE_URL` (default `https://jsonplaceholder.typicode.com`) and cover GET, POST, PUT, and DELETE, including status/body assertions, user response models, business-value lookup, and deep JSON mismatch paths. JSONPlaceholder simulates writes and does not persist mutations. The SauceDemo UI suite covers login (three JSON-driven datasets), product listing and details, cart add/remove, sorting, checkout, a separate-window flow, and sessionStorage save/restore. UI examples use semantic locators, locator and URL waits, and load-state waits; no fixed sleeps are used. Login cases are loaded with `json.load()` from `testdata/login_data.json`; `testdata/registration_data.json` is an example data file for extending the framework.

The sessionStorage helpers operate on browser-tab storage and can save captured values as JSON. Cookies and `page.context.cookies()` represent HTTP cookies, which are sent with requests to a host; `sessionStorage` is a separate Web Storage API scoped to a page origin and tab, so cookies do not capture it. The sessionStorage test writes its `session_data.json` artifact into pytest's temporary directory to keep runs isolated.

`logs/automation.log` records framework startup, per-test milestones and outcomes, and failures. File logging includes DEBUG and higher; console logging shows INFO and higher. Failed UI tests also save a screenshot under `screenshots/` and a Playwright trace under `logs/`. The HTML report is written to `reports/` when the `--html` options are supplied. Generated artifacts are excluded from source control. Passwords, tokens, and SMTP credentials are not logged.

## GitHub Actions

`.github/workflows/playwright.yml` runs when a commit is pushed to `main`, when a pull request targets `main`, and when manually started from the Actions tab with **Run workflow**. It uploads `report.html` and available screenshots/traces even when tests fail. Configure these GitHub Actions secrets for email notifications: `SMTP_HOST`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`, and `EMAIL_TO`. Optional `EMAIL_FROM` is used as the sender; otherwise the username is used. Optional Actions variables `SMTP_PORT` and `SMTP_USE_TLS` default to `587` and `true`.

The email includes the test outcome, repository/workflow/run information, the report artifact URL, and attaches `report.html` when it was generated. On fork pull requests or repositories without SMTP secrets, the workflow logs a warning and skips email rather than exposing or inventing credentials.

## Email notifications

Local pytest email summaries are disabled unless `SMTP_HOST` and `EMAIL_TO` are set. Configure these environment variables to send a run summary; credentials should be supplied through the CI secret store, never committed:

```text
SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
SMTP_FROM, EMAIL_TO, SMTP_USE_TLS
```

`SMTP_USE_TLS=true` enables STARTTLS. The default SMTP port is 587. Notification failures are logged and do not change the test result.
For local pytest-session email, use `SMTP_USERNAME` and `SMTP_PASSWORD`. The GitHub Actions workflow maps its `EMAIL_USERNAME` and `EMAIL_PASSWORD` secrets to these settings only in the email step.

## CI

The GitHub Actions workflow in `.github/workflows/playwright.yml` runs on pushes to `main`, pull requests targeting `main`, and manual dispatch. It publishes `report.html` and uploads available screenshots and traces even when tests fail. See the GitHub Actions section above for email secrets and trigger behavior.