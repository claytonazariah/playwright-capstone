from playwright.sync_api import Locator, Page


class ProductsPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.product_items: Locator = page.locator(".inventory_item")
        self.cart_badge = page.locator(".shopping_cart_badge")
        self.sort_control = page.get_by_role("combobox")

    def wait_until_open(self) -> None:
        self.product_items.first.wait_for(state="visible")

    def product_count(self) -> int:
        return self.product_items.count()

    def add_to_cart(self, product_name: str) -> None:
        self.product_card(product_name).get_by_role("button", name="Add to cart").click()

    def open_cart(self) -> None:
        self.page.locator(".shopping_cart_link").click()

    def open_product_details(self, product_name: str) -> None:
        self.page.get_by_text(product_name, exact=True).click()

    def sort_by(self, option_label: str) -> None:
        self.sort_control.select_option(label=option_label)

    def product_prices(self) -> list[str]:
        return self.page.locator(".inventory_item_price").all_inner_texts()

    def product_card(self, product_name: str) -> Locator:
        return self.product_items.filter(has_text=product_name)