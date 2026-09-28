from decimal import Decimal

import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.product_details_page import ProductDetailsPage
from pages.products_page import ProductsPage


@pytest.mark.smoke
@pytest.mark.regression
def test_add_product_updates_cart_count(logged_in_page: Page) -> None:
    products_page = ProductsPage(logged_in_page)
    products_page.add_to_cart("Sauce Labs Backpack")

    expect(products_page.cart_badge).to_have_text("1")
    products_page.open_cart()
    expect(CartPage(logged_in_page).item_names).to_have_text(["Sauce Labs Backpack"])


@pytest.mark.regression
def test_remove_product_from_cart(logged_in_page: Page) -> None:
    products_page = ProductsPage(logged_in_page)
    products_page.add_to_cart("Sauce Labs Backpack")
    products_page.open_cart()
    cart_page = CartPage(logged_in_page)

    cart_page.remove_item("Sauce Labs Backpack")

    expect(cart_page.item_names).to_have_count(0)
    expect(cart_page.cart_badge).to_have_count(0)


@pytest.mark.regression
@pytest.mark.readonly
def test_product_details_are_displayed(logged_in_page: Page) -> None:
    products_page = ProductsPage(logged_in_page)
    products_page.open_product_details("Sauce Labs Backpack")
    details_page = ProductDetailsPage(logged_in_page)
    details_page.wait_until_open()

    expect(details_page.name).to_have_text("Sauce Labs Backpack")
    expect(details_page.description).to_be_visible()
    expect(details_page.price).to_have_text("$29.99")


@pytest.mark.regression
@pytest.mark.readonly
def test_products_can_be_sorted_by_price(logged_in_page: Page) -> None:
    products_page = ProductsPage(logged_in_page)
    products_page.sort_by("Price (low to high)")

    prices = products_page.product_prices()
    assert prices == sorted(prices, key=lambda price: Decimal(price.removeprefix("$")))