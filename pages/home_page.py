import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    SECTION_TITLES = (By.CSS_SELECTOR, ".card-body h5")

    @allure.step("Открыть главную страницу DemoQA")
    def open(self):
        return self.open_path()

    @allure.step("Получить названия разделов на главной странице")
    def section_names(self):
        return [
            element.text.strip()
            for element in self.visible_elements(self.SECTION_TITLES)
        ]
