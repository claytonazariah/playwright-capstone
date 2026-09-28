import json
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.products_page import ProductsPage


LOGIN_DATA_PATH = Path(__file__).resolve().parents[2] / "testdata" / "login_data.json"
with LOGIN_DATA_PATH.open(encoding="utf-8") as login_data_file:
    LOGIN_DATA = json.load(login_data_file)


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.readonly
@pytest.mark.parametrize("scenario", LOGIN_DATA, ids=lambda scenario: scenario["case"])
def test_login_scenarios(
    page: Page, app_base_url: str, ui_diagnostics: None, scenario: dict[str, Any]
) -> None:
    login_page = LoginPage(page)
    login_page.open(app_base_url)
    login_page.login(scenario["username"], scenario["password"])

    if scenario["expected_success"]:
        page.wait_for_url("**/inventory.html")
        page.wait_for_load_state("domcontentloaded")
        products_page = ProductsPage(page)
        products_page.wait_until_open()
        assert products_page.product_count() == 6
    else:
        expect(login_page.error_message).to_contain_text(scenario["expected_error"])


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.readonly
def test_products_are_visible(logged_in_page: Page) -> None:
    products_page = ProductsPage(logged_in_page)
    expect(products_page.product_items).to_have_count(6)
    assert products_page.product_count() == 6