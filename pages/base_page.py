import os
from urllib.parse import urljoin

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip("/") + "/"
        self.wait = WebDriverWait(driver, int(os.getenv("DEMOQA_UI_WAIT_SECONDS", "20")))

    def open_path(self, path=""):
        self.driver.get(urljoin(self.base_url, path.lstrip("/")))
        return self

    def visible(self, locator):
        return self.wait.until(ec.visibility_of_element_located(locator))

    def click(self, locator):
        def click_visible(driver):
            for element in driver.find_elements(*locator):
                try:
                    if not element.is_displayed() or not element.is_enabled():
                        continue
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'})", element
                    )
                    element.click()
                    return True
                except (
                    ElementClickInterceptedException,
                    ElementNotInteractableException,
                    StaleElementReferenceException,
                ):
                    return False
            return False

        self.wait.until(click_visible)

    def visible_elements(self, locator):
        return self.wait.until(ec.visibility_of_all_elements_located(locator))
