import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage


class ProfilePage(BasePage):
    SEARCH = (By.ID, "searchBox")
    BOOK_LINKS = (By.CSS_SELECTOR, "table tbody a[href*='/books?search=']")
    STORE_BUTTON = (By.ID, "gotoStore")
    DELETE_ALL_BUTTON = (By.XPATH, "//button[normalize-space()='Delete All Books']")
    CONFIRM_BUTTON = (By.ID, "closeSmallModal-ok")
    CANCEL_BUTTON = (By.ID, "closeSmallModal-cancel")

    @allure.step("Открыть профиль")
    def open(self):
        self.open_path("profile")
        self.visible(self.SEARCH)
        return self

    @allure.step("Открыть профиль без входа")
    def open_as_guest(self):
        self.open_path("profile")
        self.visible((By.CSS_SELECTOR, "a[href='/login']"))
        return self

    @allure.step("Проверить приглашение войти")
    def login_prompt_visible(self):
        return self.visible((By.CSS_SELECTOR, "a[href='/login']")).is_displayed()

    @allure.step("Получить названия книг в профиле")
    def book_titles(self):
        self.visible(self.SEARCH)
        return [element.text for element in self.driver.find_elements(*self.BOOK_LINKS)]

    def wait_for_count(self, count):
        self.wait.until(lambda driver: len(driver.find_elements(*self.BOOK_LINKS)) == count)
        return self

    @allure.step("Перейти из профиля в магазин")
    def go_to_store(self):
        self.click(self.STORE_BUTTON)
        self.wait.until(ec.url_contains("/books"))
        return self

    @allure.step("Удалить книгу из профиля")
    def delete_book(self, isbn):
        self.click((By.CSS_SELECTOR, f"[id='delete-record-{isbn}']"))
        self.click(self.CONFIRM_BUTTON)
        alert = self.wait.until(ec.alert_is_present())
        message = alert.text
        alert.accept()
        return message

    @allure.step("Отменить удаление книги")
    def cancel_delete_book(self, isbn):
        self.click((By.CSS_SELECTOR, f"[id='delete-record-{isbn}']"))
        self.click(self.CANCEL_BUTTON)
        self.wait.until(ec.invisibility_of_element_located(self.CANCEL_BUTTON))
        return self

    @allure.step("Удалить все книги из профиля")
    def delete_all_books(self):
        self.click(self.DELETE_ALL_BUTTON)
        resource_count = self.driver.execute_script(
            "return performance.getEntriesByType('resource').length"
        )
        self.click(self.CONFIRM_BUTTON)
        self.wait.until(
            lambda driver: driver.execute_script(
                "return performance.getEntriesByType('resource')"
                ".slice(arguments[0]).some(entry => "
                "entry.name.includes('/BookStore/v1/Books?UserId='))",
                resource_count,
            )
        )
        self.driver.refresh()
        self.visible(self.SEARCH)
        return self

    @allure.step("Отменить удаление всех книг")
    def cancel_delete_all_books(self):
        self.click(self.DELETE_ALL_BUTTON)
        self.click(self.CANCEL_BUTTON)
        self.wait.until(ec.invisibility_of_element_located(self.CANCEL_BUTTON))
        return self
