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
source .venv/bin/activate
python -m pip install -r requirements.txt
playwright install chromium
```

On Linux CI, install browser system dependencies with `playwright install --with-deps chromium`.

## Run tests

```bash
# Full suite, including HTML report
pytest --html=reports/report.html --self-contained-html

# Smoke, regression, or read-only subsets
pytest -m smoke
pytest -m regression
pytest -m readonly
pytest -m "smoke or regression"

# Parallel execution
pytest -n 2

# Run UI tests against a different compatible practice site
APP_BASE_URL=https://www.saucedemo.com pytest tests/ui
```

API tests use `API_BASE_URL` (default `https://jsonplaceholder.typicode.com`) and cover GET, POST, PUT, and DELETE, including status/body assertions, user response models, business-value lookup, and deep JSON mismatch paths. JSONPlaceholder simulates writes and does not persist mutations. The SauceDemo UI suite covers login (three JSON-driven datasets), product listing and details, cart add/remove, sorting, checkout, a separate-window flow, and sessionStorage save/restore. UI examples use semantic locators, locator and URL waits, and load-state waits; no fixed sleeps are used. Login cases are loaded with `json.load()` from `testdata/login_data.json`; `testdata/registration_data.json` is an example data file for extending the framework.

The sessionStorage helpers operate on browser-tab storage and can save captured values as JSON. Cookies and `page.context.cookies()` represent HTTP cookies, which are sent with requests to a host; `sessionStorage` is a separate Web Storage API scoped to a page origin and tab, so cookies do not capture it. The sessionStorage test writes its `session_data.json` artifact into pytest's temporary directory to keep runs isolated.

`logs/automation.log` records framework startup, per-test milestones and outcomes, and failures. File logging includes DEBUG and higher; console logging shows INFO and higher. Failed UI tests also save a screenshot under `screenshots/` and a Playwright trace under `logs/`. The HTML report is written to `reports/` when the `--html` options are supplied. Generated artifacts are excluded from source control. Passwords, tokens, and SMTP credentials are not logged.

## Email notifications

Email is disabled unless `SMTP_HOST` and `EMAIL_TO` are set. Configure these environment variables to send a run summary; credentials should be supplied through the CI secret store, never committed:

```text
SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
SMTP_FROM, EMAIL_TO, SMTP_USE_TLS
```

`SMTP_USE_TLS=true` enables STARTTLS. The default SMTP port is 587. Notification failures are logged and do not change the test result.

## CI

The GitHub Actions workflow runs the suite on pushes, pull requests, and manual dispatches. It runs tests in parallel, publishes an HTML report, and uploads reports, screenshots, and traces even when tests fail. Add the SMTP values above as repository secrets or variables to enable CI email notifications.