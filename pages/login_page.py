import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "userName")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login")

    @allure.step("Открыть страницу входа")
    def open(self):
        self.open_path("login")
        self.visible(self.USERNAME)
        return self

    @allure.step("Войти в аккаунт")
    def login(self, username, password):
        self.visible(self.USERNAME).send_keys(username)
        self.visible(self.PASSWORD).send_keys(password)
        self.click(self.LOGIN_BUTTON)
        self.wait.until(ec.url_contains("/profile"))
        return self
