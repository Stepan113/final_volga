import os
from urllib.parse import urljoin

import allure


class ApiClient:
    def __init__(self, base_url, session, timeout=None):
        self.base_url = base_url.rstrip("/") + "/"
        self.session = session
        self.timeout = timeout if timeout is not None else float(
            os.getenv("DEMOQA_API_TIMEOUT_SECONDS", "15")
        )

    def request(self, method, path, **kwargs):
        with allure.step(f"Отправить {method.upper()} {path}"):
            response = self.session.request(
                method,
                urljoin(self.base_url, path.lstrip("/")),
                timeout=self.timeout,
                **kwargs,
            )
            allure.attach(
                str(response.status_code),
                name="HTTP-статус",
                attachment_type=allure.attachment_type.TEXT,
            )
            return response
