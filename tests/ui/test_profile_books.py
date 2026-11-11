import allure
import pytest

from pages.book_detail_page import BookDetailPage
from pages.book_store_page import BookStorePage
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage


pytestmark = pytest.mark.ui


def seed_books(api_client, account, auth_headers, isbns):
    response = api_client.request(
        "POST", "/BookStore/v1/Books",
        json={
            "userId": account["id"],
            "collectionOfIsbns": [{"isbn": isbn} for isbn in isbns],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, (
        f"Не удалось подготовить книги: HTTP {response.status_code}: {response.text}"
    )


def login_profile(driver, base_url, account):
    LoginPage(driver, base_url).open().login(account["username"], account["password"])
    return ProfilePage(driver, base_url)


@allure.epic("DemoQA UI")
@allure.feature("Профиль")
@allure.title("Профиль нового пользователя пуст")
def test_new_profile_is_empty(logged_in_profile):
    profile = logged_in_profile.open().wait_for_count(0)

    with allure.step("Проверить список книг"):
        assert profile.book_titles() == [], "У нового пользователя появились книги"


@allure.epic("DemoQA UI")
@allure.feature("Профиль")
@allure.title("Профиль предлагает войти гостю")
def test_profile_requires_login(driver, base_url):
    profile = ProfilePage(driver, base_url).open_as_guest()

    with allure.step("Проверить ссылку входа"):
        assert profile.login_prompt_visible(), "Гость не видит приглашение войти"


@allure.epic("DemoQA UI")
@allure.feature("Профиль")
@allure.title("В профиле отображаются добавленные книги")
def test_profile_shows_books(
    driver, base_url, api_client, account, auth_headers, catalog_books
):
    books = catalog_books[:2]
    seed_books(api_client, account, auth_headers, [book["isbn"] for book in books])
    profile = login_profile(driver, base_url, account).wait_for_count(2)

    with allure.step("Проверить две книги в профиле"):
        assert set(profile.book_titles()) == {book["title"] for book in books}


@allure.epic("DemoQA UI")
@allure.feature("Добавление книг")
@allure.title("Пользователь добавляет одну книгу через UI")
def test_add_one_book_ui(logged_in_profile, driver, base_url, catalog_books):
    book = catalog_books[0]
    logged_in_profile.go_to_store()
    BookStorePage(driver, base_url).open_book(book["isbn"])
    message = BookDetailPage(driver, base_url).add_to_collection()
    profile = ProfilePage(driver, base_url).open().wait_for_count(1)

    with allure.step("Проверить подтверждение и книгу в профиле"):
        assert "added" in message.lower(), f"Неожиданное сообщение: {message}"
        assert profile.book_titles() == [book["title"]]


@allure.epic("DemoQA UI")
@allure.feature("Добавление книг")
@allure.title("Пользователь добавляет три книги через UI")
def test_add_multiple_books_ui(logged_in_profile, driver, base_url, catalog_books):
    books = catalog_books[:3]
    store = BookStorePage(driver, base_url)
    detail = BookDetailPage(driver, base_url)
    logged_in_profile.go_to_store()

    for book in books:
        store.open().open_book(book["isbn"])
        message = detail.add_to_collection()
        assert "added" in message.lower(), f"Не удалось добавить {book['title']}: {message}"

    profile = ProfilePage(driver, base_url).open().wait_for_count(3)
    with allure.step("Проверить все три книги в профиле"):
        assert set(profile.book_titles()) == {book["title"] for book in books}


@allure.epic("DemoQA UI")
@allure.feature("Добавление книг")
@allure.title("UI не добавляет уже имеющуюся книгу повторно")
def test_duplicate_book_ui(
    driver, base_url, api_client, account, auth_headers, catalog_books
):
    book = catalog_books[0]
    seed_books(api_client, account, auth_headers, [book["isbn"]])
    login_profile(driver, base_url, account)
    BookStorePage(driver, base_url).open().open_book(book["isbn"])
    message = BookDetailPage(driver, base_url).add_to_collection()
    profile = ProfilePage(driver, base_url).open().wait_for_count(1)

    with allure.step("Проверить отказ и отсутствие дубля"):
        assert "already present" in message.lower(), f"Неожиданное сообщение: {message}"
        assert profile.book_titles() == [book["title"]]


@allure.epic("DemoQA UI")
@allure.feature("Удаление книг")
@allure.title("Пользователь удаляет одну книгу через UI")
def test_delete_one_book_ui(
    driver, base_url, api_client, account, auth_headers, catalog_books
):
    books = catalog_books[:2]
    seed_books(api_client, account, auth_headers, [book["isbn"] for book in books])
    profile = login_profile(driver, base_url, account).wait_for_count(2)
    message = profile.delete_book(books[0]["isbn"])
    profile.wait_for_count(1)

    with allure.step("Проверить подтверждение и оставшуюся книгу"):
        assert "deleted" in message.lower(), f"Неожиданное сообщение: {message}"
        assert profile.book_titles() == [books[1]["title"]]


@allure.epic("DemoQA UI")
@allure.feature("Удаление книг")
@allure.title("Отмена удаления сохраняет книгу в профиле")
def test_cancel_delete_book_ui(
    driver, base_url, api_client, account, auth_headers, catalog_books
):
    book = catalog_books[0]
    seed_books(api_client, account, auth_headers, [book["isbn"]])
    profile = login_profile(driver, base_url, account).wait_for_count(1)
    profile.cancel_delete_book(book["isbn"])

    with allure.step("Проверить сохранность книги"):
        assert profile.book_titles() == [book["title"]]


@allure.epic("DemoQA UI")
@allure.feature("Удаление книг")
@allure.title("Пользователь удаляет все книги через UI")
def test_delete_all_books_ui(
    driver, base_url, api_client, account, auth_headers, catalog_books
):
    books = catalog_books[:3]
    seed_books(api_client, account, auth_headers, [book["isbn"] for book in books])
    profile = login_profile(driver, base_url, account).wait_for_count(3)
    profile.delete_all_books().wait_for_count(0)

    with allure.step("Проверить пустой профиль после удаления"):
        assert profile.book_titles() == []


@allure.epic("DemoQA UI")
@allure.feature("Удаление книг")
@allure.title("Отмена удаления всех книг сохраняет коллекцию")
def test_cancel_delete_all_books_ui(
    driver, base_url, api_client, account, auth_headers, catalog_books
):
    books = catalog_books[:2]
    seed_books(api_client, account, auth_headers, [book["isbn"] for book in books])
    profile = login_profile(driver, base_url, account).wait_for_count(2)
    profile.cancel_delete_all_books()

    with allure.step("Проверить сохранность коллекции"):
        assert set(profile.book_titles()) == {book["title"] for book in books}
