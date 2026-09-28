from playwright.sync_api import Page


class ProductDetailsPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.name = page.locator(".inventory_details_name")
        self.description = page.locator(".inventory_details_desc")
        self.price = page.locator(".inventory_details_price")

    def wait_until_open(self) -> None:
        self.name.wait_for(state="visible")