import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import APIRequestContext, Playwright, Page

from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from utils.email_notifier import send_email
from utils.logger import get_logger


ROOT_DIR = Path(__file__).parent
logger = get_logger(__name__)


def pytest_configure(config: pytest.Config) -> None:
    (ROOT_DIR / "logs").mkdir(exist_ok=True)
    (ROOT_DIR / "screenshots").mkdir(exist_ok=True)
    logger.debug("Pytest configured; automation log: %s", ROOT_DIR / "logs" / "automation.log")


def pytest_sessionstart(session: pytest.Session) -> None:
    if hasattr(session.config, "workerinput"):
        return
    logger.info("Test session started")


def pytest_runtest_setup(item: pytest.Item) -> None:
    logger.debug("Starting test: %s", item.nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
    if report.when == "call":
        if report.passed:
            logger.info("Test passed: %s", item.nodeid)
        elif report.failed:
            logger.error("Test failed: %s", item.nodeid)
    elif report.failed:
        logger.error("Test failed during %s phase: %s", report.when, item.nodeid)


@pytest.fixture
def app_base_url() -> str:
    return os.getenv("APP_BASE_URL", "https://www.saucedemo.com").rstrip("/")


@pytest.fixture
def logged_in_page(page: Page, app_base_url: str, ui_diagnostics: None) -> Page:
    logger.debug("Opening UI test session at %s", app_base_url)
    login_page = LoginPage(page)
    login_page.open(app_base_url)
    login_page.login("standard_user", "secret_sauce")
    page.wait_for_url("**/inventory.html")
    page.wait_for_load_state("domcontentloaded")
    ProductsPage(page).wait_until_open()
    logger.info("UI test session reached the inventory page")
    return page


@pytest.fixture
def api_context(playwright: Playwright) -> APIRequestContext:
    base_url = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com")
    logger.debug("Creating API request context for %s", base_url)
    context = playwright.request.new_context(
        base_url=base_url.rstrip("/"),
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture
def ui_diagnostics(page: Page, request: pytest.FixtureRequest) -> None:
    page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
    logger.debug("Started browser trace for %s", request.node.nodeid)
    yield

    report = getattr(request.node, "rep_call", None)
    if report is None or not report.failed:
        page.context.tracing.stop()
        return

    artifact_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)[:180]
    screenshot_path = ROOT_DIR / "screenshots" / f"{artifact_name}.png"
    trace_path = ROOT_DIR / "logs" / f"{artifact_name}.zip"
    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info("Saved failure screenshot: %s", screenshot_path)
    except Exception:
        logger.exception("Could not save screenshot for %s", request.node.nodeid)
    try:
        page.context.tracing.stop(path=str(trace_path))
        logger.info("Saved failure trace: %s", trace_path)
    except Exception:
        logger.exception("Could not save trace for %s", request.node.nodeid)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if hasattr(session.config, "workerinput"):
        return

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    stats = getattr(reporter, "stats", {})
    counts = {
        result: len(stats.get(result, []))
        for result in ("passed", "failed", "error", "skipped", "xfailed", "xpassed")
    }
    summary = ", ".join(f"{name}: {count}" for name, count in counts.items())
    outcome = "PASSED" if exitstatus == pytest.ExitCode.OK else "FAILED"
    logger.info("Test session finished: %s (exit status %s); %s", outcome, exitstatus, summary)

    smtp_host = os.getenv("SMTP_HOST")
    email_to = os.getenv("EMAIL_TO")
    if not smtp_host and not email_to:
        logger.debug("Email notification is not configured; skipping")
        return
    if not smtp_host or not email_to:
        logger.warning("Email notification configuration is incomplete; skipping")
        return

    try:
        send_email(f"{outcome}: Playwright test run", summary)
        logger.info("Test summary email sent")
    except Exception:
        logger.exception("Could not send test summary email")