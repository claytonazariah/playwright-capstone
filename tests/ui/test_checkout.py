import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.products_page import ProductsPage


@pytest.mark.regression
def test_checkout_completes_order(logged_in_page: Page) -> None:
    products_page = ProductsPage(logged_in_page)
    products_page.add_to_cart("Sauce Labs Backpack")
    products_page.open_cart()
    CartPage(logged_in_page).checkout()

    checkout_page = CheckoutPage(logged_in_page)
    checkout_page.complete_information("Taylor", "Morgan", "12345")
    logged_in_page.wait_for_url("**/checkout-step-two.html")
    checkout_page.finish_order()
    logged_in_page.wait_for_url("**/checkout-complete.html")

    expect(checkout_page.confirmation).to_have_text("Thank you for your order!")