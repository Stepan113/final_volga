import os
from uuid import uuid4

import allure
import pytest
import requests
from jsonschema import validate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from swagger.client import ApiClient
from swagger.schemas import CATALOG_SCHEMA


def pytest_addoption(parser):
    parser.addoption("--base-url", default=os.getenv("DEMOQA_BASE_URL", "https://demoqa.com"))
    parser.addoption("--api-base-url", default=os.getenv("DEMOQA_API_BASE_URL", "https://demoqa.com"))
    parser.addoption(
        "--browser",
        choices=("chrome", "firefox", "edge"),
        default=os.getenv("DEMOQA_BROWSER", "chrome").lower(),
    )
    parser.addoption("--headed", action="store_true", help="Show the browser window.")
    parser.addoption("--headless", action="store_true", help="Explicitly run headless (the default).")


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url").rstrip("/")


@pytest.fixture
def driver(request):
    browser_name = request.config.getoption("--browser")
    headed = request.config.getoption("--headed")

    if browser_name == "chrome":
        options = ChromeOptions()
        if not headed:
            options.add_argument("--headless=new")
        if binary := os.getenv("CHROME_BINARY"):
            options.binary_location = binary
        if os.getenv("CHROME_NO_SANDBOX") == "1":
            options.add_argument("--no-sandbox")
        if profile := os.getenv("CHROME_USER_DATA_DIR"):
            options.add_argument(f"--user-data-dir={profile}-{uuid4().hex[:8]}")
        browser = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = FirefoxOptions()
        if not headed:
            options.add_argument("-headless")
        if binary := os.getenv("FIREFOX_BINARY"):
            options.binary_location = binary
        browser = webdriver.Firefox(options=options)
    else:
        options = EdgeOptions()
        if not headed:
            options.add_argument("--headless=new")
        if binary := os.getenv("EDGE_BINARY"):
            options.binary_location = binary
        browser = webdriver.Edge(options=options)

    browser.set_window_size(1440, 1000)
    try:
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def api_client(request):
    with requests.Session() as session:
        yield ApiClient(request.config.getoption("--api-base-url"), session)


@pytest.fixture
def catalog_books(api_client):
    response = api_client.request("GET", "/BookStore/v1/Books")
    assert response.status_code == 200, f"Каталог: HTTP {response.status_code}: {response.text}"
    body = response.json()
    validate(body, CATALOG_SCHEMA)
    assert len(body["books"]) >= 3, "Для сценариев нужны минимум три книги в магазине"
    return body["books"]


@pytest.fixture
def account(api_client):
    username = f"qa_{uuid4().hex[:16]}"
    password = f"Qa1!{uuid4().hex}"
    registration = api_client.request(
        "POST", "/Account/v1/User", json={"userName": username, "password": password}
    )
    assert registration.status_code == 201, (
        f"Не удалось создать временного пользователя: HTTP {registration.status_code}: "
        f"{registration.text}"
    )
    user_id = registration.json().get("userID") or registration.json()["userId"]

    token_response = api_client.request(
        "POST", "/Account/v1/GenerateToken",
        json={"userName": username, "password": password},
    )
    assert token_response.status_code == 200, "Не удалось получить токен"
    token = token_response.json()["token"]
    user = {"id": user_id, "username": username, "password": password, "token": token}
    try:
        yield user
    finally:
        fresh_token_response = api_client.request(
            "POST", "/Account/v1/GenerateToken",
            json={"userName": username, "password": password},
        )
        cleanup_token = fresh_token_response.json().get("token", token)
        deletion = api_client.request(
            "DELETE", f"/Account/v1/User/{user_id}",
            headers={"Authorization": f"Bearer {cleanup_token}"},
        )
        assert deletion.status_code == 204, (
            f"Не удалось удалить временного пользователя {user_id}: "
            f"HTTP {deletion.status_code}"
        )


@pytest.fixture
def logged_in_profile(driver, base_url, account):
    from pages.login_page import LoginPage
    from pages.profile_page import ProfilePage

    LoginPage(driver, base_url).open().login(account["username"], account["password"])
    return ProfilePage(driver, base_url)


@pytest.fixture
def auth_headers(account):
    return {"Authorization": f"Bearer {account['token']}"}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when not in ("setup", "call") or not report.failed:
        return

    browser = item.funcargs.get("driver")
    if browser is None:
        return

    try:
        allure.attach(
            browser.get_screenshot_as_png(),
            name="Скриншот при ошибке",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as exc:
        allure.attach(
            f"Не удалось получить скриншот: {exc}",
            name="Ошибка снятия скриншота",
            attachment_type=allure.attachment_type.TEXT,
        )
