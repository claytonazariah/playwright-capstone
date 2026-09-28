from playwright.sync_api import Locator, Page


class CartPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.cart_items: Locator = page.locator(".cart_item")
        self.item_names: Locator = page.locator(".cart_item .inventory_item_name")
        self.cart_badge: Locator = page.locator(".shopping_cart_badge")
        self.checkout_button = page.get_by_role("button", name="Checkout")

    def remove_item(self, product_name: str) -> None:
        cart_item = self.cart_items.filter(has_text=product_name)
        cart_item.get_by_role("button", name="Remove").click()

    def checkout(self) -> None:
        self.checkout_button.click()