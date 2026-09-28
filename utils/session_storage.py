from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page

from utils.json_utils import read_json, write_json


def write_session_value(page: Page, key: str, value: str) -> None:
    page.evaluate("([key, value]) => sessionStorage.setItem(key, value)", [key, value])


def read_session_value(page: Page, key: str) -> str | None:
    return page.evaluate("(key) => sessionStorage.getItem(key)", key)


def read_session_data(page: Page) -> dict[str, str]:
    return page.evaluate("() => Object.fromEntries(Object.entries(sessionStorage))")


def save_session_data(page: Page, path: str | Path) -> dict[str, str]:
    session_data = read_session_data(page)
    write_json(path, session_data)
    return session_data


def clear_session_storage(page: Page) -> None:
    page.evaluate("() => sessionStorage.clear()")


def restore_session_data(page: Page, path: str | Path) -> None:
    session_data: Any = read_json(path)
    if not isinstance(session_data, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in session_data.items()
    ):
        raise ValueError("Session data must be a JSON object containing only string keys and values")
    page.evaluate(
        "(data) => Object.entries(data).forEach(([key, value]) => sessionStorage.setItem(key, value))",
        session_data,
    )


def validate_session_data(page: Page, expected: dict[str, str]) -> bool:
    return read_session_data(page) == expected

def save_session(page: Page, path: str | Path) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    page.context.storage_state(path=str(state_path))


def new_context_with_session(browser: Browser, path: str | Path) -> BrowserContext:
    state_path = Path(path)
    if not state_path.is_file():
        raise FileNotFoundError(f"Storage state file does not exist: {state_path}")
    return browser.new_context(storage_state=str(state_path))