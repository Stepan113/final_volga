import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage


class BookStorePage(BasePage):
    SEARCH = (By.ID, "searchBox")
    BOOK_LINKS = (By.CSS_SELECTOR, "table tbody a[href*='/books?search=']")

    @allure.step("Открыть магазин книг")
    def open(self):
        self.open_path("books")
        self.visible(self.SEARCH)
        return self

    @allure.step("Получить названия книг в магазине")
    def book_titles(self):
        self.visible(self.SEARCH)
        return [element.text for element in self.driver.find_elements(*self.BOOK_LINKS)]

    @allure.step("Найти книгу в магазине")
    def search(self, query):
        field = self.visible(self.SEARCH)
        field.clear()
        field.send_keys(query)
        return self

    def wait_for_count(self, count):
        self.wait.until(lambda driver: len(driver.find_elements(*self.BOOK_LINKS)) == count)
        return self

    @allure.step("Открыть карточку книги")
    def open_book(self, isbn):
        link = (By.CSS_SELECTOR, f"a[href='/books?search={isbn}']")
        self.click(link)
        self.wait.until(ec.url_contains(f"search={isbn}"))
        return self
