import json

import pytest
from playwright.sync_api import Page

from utils.session_storage import (
    clear_session_storage,
    read_session_value,
    restore_session_data,
    save_session_data,
    validate_session_data,
    write_session_value,
)


@pytest.mark.regression
@pytest.mark.readonly
def test_session_storage_can_be_saved_cleared_and_restored(
    logged_in_page: Page, tmp_path
) -> None:
    expected = {"framework-session": "session-value", "framework-mode": "test"}
    data_path = tmp_path / "session_data.json"

    for key, value in expected.items():
        write_session_value(logged_in_page, key, value)

    assert read_session_value(logged_in_page, "framework-session") == "session-value"
    assert validate_session_data(logged_in_page, expected)
    assert save_session_data(logged_in_page, data_path) == expected
    assert json.loads(data_path.read_text(encoding="utf-8")) == expected

    clear_session_storage(logged_in_page)
    assert read_session_value(logged_in_page, "framework-session") is None

    restore_session_data(logged_in_page, data_path)
    assert validate_session_data(logged_in_page, expected)