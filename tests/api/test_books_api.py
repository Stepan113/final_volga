import allure
import pytest
from jsonschema import validate

from swagger.schemas import (
    ADDED_BOOKS_SCHEMA,
    CATALOG_SCHEMA,
    ERROR_SCHEMA,
    PROFILE_SCHEMA,
)


pytestmark = [pytest.mark.api, allure.epic("DemoQA API")]


def profile_books(api_client, account, auth_headers):
    response = api_client.request(
        "GET", f"/Account/v1/User/{account['id']}", headers=auth_headers
    )
    assert response.status_code == 200, f"Профиль: HTTP {response.status_code}"
    body = response.json()
    validate(body, PROFILE_SCHEMA)
    return body["books"]


def add_books(api_client, account, auth_headers, isbns):
    return api_client.request(
        "POST",
        "/BookStore/v1/Books",
        json={
            "userId": account["id"],
            "collectionOfIsbns": [{"isbn": isbn} for isbn in isbns],
        },
        headers=auth_headers,
    )


@allure.feature("Каталог магазина")
@allure.title("API возвращает список книг магазина")
def test_store_catalog(api_client):
    response = api_client.request("GET", "/BookStore/v1/Books")

    with allure.step("Проверить HTTP-статус и JSON каталога"):
        assert response.status_code == 200, f"Ожидался HTTP 200, получен {response.status_code}"
        body = response.json()
        validate(body, CATALOG_SCHEMA)
        assert body["books"], "Каталог магазина пуст"


@allure.feature("Каталог магазина")
@allure.title("API сообщает об отсутствии книги с неизвестным ISBN")
def test_unknown_store_book(api_client):
    response = api_client.request(
        "GET", "/BookStore/v1/Book", params={"ISBN": "unknown-isbn"}
    )

    with allure.step("Проверить ошибку и её JSON"):
        assert response.status_code == 400, f"Ожидался HTTP 400, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)


@allure.feature("Профиль")
@allure.title("Новый пользователь имеет пустой список книг")
def test_empty_profile(api_client, account, auth_headers):
    with allure.step("Получить список книг нового пользователя"):
        assert profile_books(api_client, account, auth_headers) == [], (
            "У нового пользователя должны отсутствовать книги"
        )


@allure.feature("Профиль")
@allure.title("Профиль недоступен без авторизации")
def test_profile_without_authorization(api_client, account):
    response = api_client.request("GET", f"/Account/v1/User/{account['id']}")

    with allure.step("Проверить отказ и JSON ошибки"):
        assert response.status_code == 401, f"Ожидался HTTP 401, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)


@allure.feature("Добавление книг")
@allure.title("API добавляет одну книгу в профиль")
def test_add_one_book(api_client, account, auth_headers, catalog_books):
    isbn = catalog_books[0]["isbn"]
    response = add_books(api_client, account, auth_headers, [isbn])

    with allure.step("Проверить ответ добавления и книгу в профиле"):
        assert response.status_code == 201, f"Ожидался HTTP 201, получен {response.status_code}"
        validate(response.json(), ADDED_BOOKS_SCHEMA)
        assert {book["isbn"] for book in profile_books(api_client, account, auth_headers)} == {isbn}


@allure.feature("Добавление книг")
@allure.title("API добавляет несколько книг в профиль")
def test_add_multiple_books(api_client, account, auth_headers, catalog_books):
    isbns = [book["isbn"] for book in catalog_books[:3]]
    response = add_books(api_client, account, auth_headers, isbns)

    with allure.step("Проверить ответ и все три книги в профиле"):
        assert response.status_code == 201, f"Ожидался HTTP 201, получен {response.status_code}"
        validate(response.json(), ADDED_BOOKS_SCHEMA)
        assert {book["isbn"] for book in profile_books(api_client, account, auth_headers)} == set(isbns)


@allure.feature("Добавление книг")
@allure.title("API отклоняет повторное добавление книги")
def test_add_duplicate_book(api_client, account, auth_headers, catalog_books):
    isbn = catalog_books[0]["isbn"]
    first = add_books(api_client, account, auth_headers, [isbn])
    assert first.status_code == 201, "Не удалось подготовить книгу для проверки"

    response = add_books(api_client, account, auth_headers, [isbn])
    with allure.step("Проверить ошибку и неизменность коллекции"):
        assert response.status_code == 400, f"Ожидался HTTP 400, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)
        assert {book["isbn"] for book in profile_books(api_client, account, auth_headers)} == {isbn}


@allure.feature("Добавление книг")
@allure.title("API отклоняет неизвестный ISBN")
def test_add_unknown_book(api_client, account, auth_headers):
    response = add_books(api_client, account, auth_headers, ["unknown-isbn"])

    with allure.step("Проверить ошибку и пустой профиль"):
        assert response.status_code == 400, f"Ожидался HTTP 400, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)
        assert profile_books(api_client, account, auth_headers) == []


@allure.feature("Удаление книг")
@allure.title("API удаляет одну книгу и сохраняет остальные")
def test_delete_one_book(api_client, account, auth_headers, catalog_books):
    isbns = [book["isbn"] for book in catalog_books[:2]]
    assert add_books(api_client, account, auth_headers, isbns).status_code == 201
    response = api_client.request(
        "DELETE", "/BookStore/v1/Book",
        json={"userId": account["id"], "isbn": isbns[0]},
        headers=auth_headers,
    )

    with allure.step("Проверить HTTP 204, пустое тело и оставшуюся книгу"):
        assert response.status_code == 204, f"Ожидался HTTP 204, получен {response.status_code}"
        assert not response.content, "Ответ HTTP 204 должен быть пустым"
        assert {book["isbn"] for book in profile_books(api_client, account, auth_headers)} == {isbns[1]}


@allure.feature("Удаление книг")
@allure.title("API отклоняет удаление отсутствующей книги")
def test_delete_missing_book(api_client, account, auth_headers, catalog_books):
    isbn = catalog_books[0]["isbn"]
    response = api_client.request(
        "DELETE", "/BookStore/v1/Book",
        json={"userId": account["id"], "isbn": isbn},
        headers=auth_headers,
    )

    with allure.step("Проверить ошибку и пустой профиль"):
        assert response.status_code == 400, f"Ожидался HTTP 400, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)
        assert profile_books(api_client, account, auth_headers) == []


@allure.feature("Удаление книг")
@allure.title("API удаляет все книги из профиля")
def test_delete_multiple_books(api_client, account, auth_headers, catalog_books):
    isbns = [book["isbn"] for book in catalog_books[:3]]
    assert add_books(api_client, account, auth_headers, isbns).status_code == 201
    response = api_client.request(
        "DELETE", "/BookStore/v1/Books",
        params={"UserId": account["id"]},
        headers=auth_headers,
    )

    with allure.step("Проверить HTTP 204 и пустой профиль"):
        assert response.status_code == 204, f"Ожидался HTTP 204, получен {response.status_code}"
        assert not response.content, "Ответ HTTP 204 должен быть пустым"
        assert profile_books(api_client, account, auth_headers) == []


@allure.feature("Удаление книг")
@allure.title("API не удаляет книги без авторизации")
def test_delete_without_authorization(api_client, account, auth_headers, catalog_books):
    isbn = catalog_books[0]["isbn"]
    assert add_books(api_client, account, auth_headers, [isbn]).status_code == 201
    response = api_client.request(
        "DELETE", "/BookStore/v1/Book",
        json={"userId": account["id"], "isbn": isbn},
    )

    with allure.step("Проверить отказ и сохранность книги"):
        assert response.status_code == 401, f"Ожидался HTTP 401, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)
        assert {book["isbn"] for book in profile_books(api_client, account, auth_headers)} == {isbn}


@allure.feature("Добавление книг")
@allure.title("API не добавляет несколько книг без авторизации")
def test_add_batch_without_authorization(api_client, account, auth_headers, catalog_books):
    isbns = [book["isbn"] for book in catalog_books[:2]]
    response = api_client.request(
        "POST", "/BookStore/v1/Books",
        json={
            "userId": account["id"],
            "collectionOfIsbns": [{"isbn": isbn} for isbn in isbns],
        },
    )

    with allure.step("Проверить отказ и пустой профиль"):
        assert response.status_code == 401, f"Ожидался HTTP 401, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)
        assert profile_books(api_client, account, auth_headers) == []


@allure.feature("Удаление книг")
@allure.title("API не удаляет весь список книг без авторизации")
def test_delete_all_without_authorization(api_client, account, auth_headers, catalog_books):
    isbns = [book["isbn"] for book in catalog_books[:2]]
    assert add_books(api_client, account, auth_headers, isbns).status_code == 201
    response = api_client.request(
        "DELETE", "/BookStore/v1/Books", params={"UserId": account["id"]}
    )

    with allure.step("Проверить отказ и сохранность обеих книг"):
        assert response.status_code == 401, f"Ожидался HTTP 401, получен {response.status_code}"
        validate(response.json(), ERROR_SCHEMA)
        assert {book["isbn"] for book in profile_books(api_client, account, auth_headers)} == set(isbns)
