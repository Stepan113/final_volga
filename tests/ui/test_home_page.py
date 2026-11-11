import allure
import pytest

from pages.home_page import HomePage


@allure.epic("DemoQA")
@allure.feature("Главная страница")
@allure.title("На главной странице доступен раздел Elements")
@pytest.mark.ui
def test_elements_section_is_visible(driver, base_url):
    home_page = HomePage(driver, base_url)
    home_page.open()

    with allure.step("Проверить наличие раздела Elements"):
        assert "Elements" in home_page.section_names()
