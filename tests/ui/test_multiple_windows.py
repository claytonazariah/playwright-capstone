import pytest
from playwright.sync_api import Page, expect


WINDOWS_URL = "https://the-internet.herokuapp.com/windows"


@pytest.mark.regression
@pytest.mark.readonly
def test_open_new_window(page: Page, ui_diagnostics: None) -> None:
    page.goto(WINDOWS_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    parent_url = page.url
    assert len(page.context.pages) == 1

    with page.context.expect_page() as child_page_info:
        page.get_by_role("link", name="Click Here").click()

    child_page = child_page_info.value
    child_page.wait_for_load_state("domcontentloaded")
    child_page.wait_for_url("**/windows/new")

    assert len(page.context.pages) == 2
    assert page.url == parent_url == WINDOWS_URL
    assert child_page.url == f"{WINDOWS_URL}/new"
    expect(child_page.get_by_role("heading", name="New Window")).to_be_visible()