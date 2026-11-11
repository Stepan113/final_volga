import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage


class BookDetailPage(BasePage):
    ADD_BUTTON = (By.XPATH, "//button[normalize-space()='Add To Your Collection']")

    @allure.step("Добавить книгу в коллекцию")
    def add_to_collection(self):
        self.click(self.ADD_BUTTON)
        alert = self.wait.until(ec.alert_is_present())
        message = alert.text
        alert.accept()
        return message
