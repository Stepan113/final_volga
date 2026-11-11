import allure
import pytest

from pages.book_store_page import BookStorePage


pytestmark = pytest.mark.ui


@allure.epic("DemoQA UI")
@allure.feature("Магазин книг")
@allure.title("В магазине отображается список книг")
def test_store_shows_books(driver, base_url, catalog_books):
    store = BookStorePage(driver, base_url).open()
    store.wait_for_count(len(catalog_books))

    with allure.step("Сравнить книги в UI и API"):
        titles = store.book_titles()
        assert set(titles) == {book["title"] for book in catalog_books}, (
            "Список книг магазина в UI отличается от API"
        )


@allure.epic("DemoQA UI")
@allure.feature("Поиск")
@allure.title("Поиск находит книгу по точному названию")
def test_search_finds_book(driver, base_url, catalog_books):
    title = catalog_books[0]["title"]
    store = BookStorePage(driver, base_url).open().search(title)
    store.wait_for_count(1)

    with allure.step("Проверить результат поиска"):
        assert store.book_titles() == [title], f"Ожидалась только книга {title}"


@allure.epic("DemoQA UI")
@allure.feature("Поиск")
@allure.title("Поиск не показывает книги по неизвестному запросу")
def test_search_unknown_book(driver, base_url):
    store = BookStorePage(driver, base_url).open().search("qa_nonexistent_book_987654321")
    store.wait_for_count(0)

    with allure.step("Проверить пустой результат"):
        assert store.book_titles() == [], "Неизвестная книга появилась в результатах поиска"
