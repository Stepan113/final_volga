import allure
import pytest
from jsonschema import validate

from pages.book_detail_page import BookDetailPage
from pages.book_store_page import BookStorePage
from pages.profile_page import ProfilePage
from swagger.schemas import PROFILE_SCHEMA


@allure.epic("DemoQA")
@allure.feature("UI + API")
@allure.title("Логин, добавление трёх книг, удаление одной и проверка профиля через API")
@pytest.mark.ui
def test_book_collection_end_to_end(
    logged_in_profile, driver, base_url, api_client, account, catalog_books
):
    books = catalog_books[:3]
    store = BookStorePage(driver, base_url)
    detail = BookDetailPage(driver, base_url)
    profile = ProfilePage(driver, base_url)

    logged_in_profile.go_to_store()
    for book in books:
        store.open().open_book(book["isbn"])
        message = detail.add_to_collection()
        assert "added" in message.lower(), f"Не удалось добавить {book['title']}: {message}"

    profile.open().wait_for_count(3)
    with allure.step("Проверить три книги перед удалением"):
        assert set(profile.book_titles()) == {book["title"] for book in books}

    message = profile.delete_book(books[0]["isbn"])
    assert "deleted" in message.lower(), f"Не удалось удалить книгу: {message}"
    profile.wait_for_count(2)

    with allure.step("Проверить две книги после удаления в UI"):
        assert set(profile.book_titles()) == {book["title"] for book in books[1:]}

    token_response = api_client.request(
        "POST", "/Account/v1/GenerateToken",
        json={"userName": account["username"], "password": account["password"]},
    )
    assert token_response.status_code == 200, "Не удалось получить токен для проверки API"
    headers = {"Authorization": f"Bearer {token_response.json()['token']}"}
    response = api_client.request(
        "GET", f"/Account/v1/User/{account['id']}", headers=headers
    )
    with allure.step("Сверить список книг профиля с API"):
        assert response.status_code == 200, f"Профиль: HTTP {response.status_code}"
        body = response.json()
        validate(body, PROFILE_SCHEMA)
        expected = {book["isbn"] for book in books[1:]}
        assert {book["isbn"] for book in body["books"]} == expected
