# DemoQA: UI и API автотесты

Проект проверяет магазин книг DemoQA: https://demoqa.com/books, профиль пользователя, поиск и Book Store API из https://demoqa.com/swagger. Тесты написаны на Python 3.12+, pytest и Selenium. Для UI используется простой Page Object Model: один класс на страницу, действия и локаторы находятся рядом; проверки остаются в тестах.

Каждый тест независим. Тесты, которым нужен пользователь, создают временный аккаунт через API и удаляют его после выполнения. Имя и пароль генерируются для каждого теста. UI и API могут запускаться параллельно.

## Требования и установка

- Python 3.12 или новее.
- Chrome, Firefox или Microsoft Edge для запуска UI-тестов. По умолчанию используется Chrome. Selenium Manager подбирает драйвер; при первом запуске ему может понадобиться сеть.
- Доступ к demoqa.com.
- Для просмотра HTML-отчётов — отдельная команда Allure Report CLI.

Из корня проекта:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt

В PyCharm выберите интерпретатор .venv/bin/python.

## Запуск тестов

    .venv/bin/python -m pytest
    .venv/bin/python -m pytest -m ui
    .venv/bin/python -m pytest -m api
    .venv/bin/python -m pytest tests/ui/test_book_store.py
    .venv/bin/python -m pytest tests/ui/test_book_store.py::test_search_finds_book

Браузер по умолчанию работает без окна. Для видимого окна:

    .venv/bin/python -m pytest -m ui --headed

Параллельный запуск в двух процессах:

    .venv/bin/python -m pytest -n 2

На внешнем DemoQA слишком много одновременных запросов могут замедлить тесты. Начните с двух процессов; каждый тест использует собственный аккаунт и браузер.

Для запуска в другом браузере:

    .venv/bin/python -m pytest -m ui --browser=firefox
    .venv/bin/python -m pytest -m ui --browser=edge

Браузер должен быть доступен на компьютере или загружен Selenium Manager. Все 15 UI-тестов проверены в Chrome, Firefox и Edge; для Firefox и Edge использовались временно загруженные копии браузеров.

## Параметры окружения

- DEMOQA_BASE_URL — адрес UI, по умолчанию https://demoqa.com.
- DEMOQA_API_BASE_URL — адрес API, по умолчанию https://demoqa.com.
- DEMOQA_BROWSER — chrome, firefox или edge; можно вместо этого передать --browser.
- DEMOQA_UI_WAIT_SECONDS — время явного ожидания элементов, по умолчанию 20 секунд.
- DEMOQA_API_TIMEOUT_SECONDS — таймаут HTTP-запроса, по умолчанию 15 секунд.
- CHROME_BINARY, FIREFOX_BINARY, EDGE_BINARY — путь к исполняемому файлу браузера, если Selenium Manager не находит его автоматически.

Параметры --base-url и --api-base-url переопределяют адреса для одного запуска. Например:

    DEMOQA_BASE_URL=https://demoqa.com .venv/bin/python -m pytest -m ui --browser=chrome

В ограниченном контейнере, где домашний каталог недоступен для записи, проверенный запуск Chrome выглядит так:

    XDG_CONFIG_HOME=/tmp/finalvolga-xdg-config \
    XDG_CACHE_HOME=/tmp/finalvolga-xdg-cache \
    SE_CACHE_PATH=/tmp/finalvolga-selenium-cache \
    CHROME_USER_DATA_DIR=/tmp/finalvolga-chrome-profile \
    CHROME_NO_SANDBOX=1 .venv/bin/python -m pytest -m ui

CHROME_NO_SANDBOX нужен только для такой ограниченной среды.

## Реализованные проверки

### API — tests/api/test_books_api.py

| Тест | Проверка |
| --- | --- |
| test_store_catalog | Каталог отвечает HTTP 200, JSON содержит книги. |
| test_unknown_store_book | Неизвестный ISBN возвращает ошибку HTTP 400. |
| test_empty_profile | У нового пользователя пустой список книг. |
| test_profile_without_authorization | Без токена профиль возвращает HTTP 401. |
| test_add_one_book | Одна книга добавляется и появляется в профиле. |
| test_add_multiple_books | Три книги добавляются и появляются в профиле. |
| test_add_duplicate_book | Повторное добавление отклоняется, дубль не возникает. |
| test_add_unknown_book | Неизвестный ISBN отклоняется, профиль остаётся пустым. |\n| test_add_batch_without_authorization | Без токена добавление нескольких книг запрещено, профиль пуст. |
| test_delete_one_book | Удаляется одна книга, другая остаётся. |
| test_delete_missing_book | Удаление отсутствующей книги возвращает HTTP 400. |
| test_delete_multiple_books | Удаляются все три книги, профиль пустеет. |
| test_delete_without_authorization | Без токена удаление запрещено, книга остаётся. |\n| test_delete_all_without_authorization | Без токена удаление всех книг запрещено, обе остаются. |

Каждый API-тест проверяет HTTP-статус и содержимое ответа. JSON с данными проверяется через jsonschema; для HTTP 204 проверяется пустое тело.

### UI — tests/ui/

| Файл | Проверки |
| --- | --- |
| test_home_page.py | На главной странице виден раздел Elements. |
| test_book_store.py | Список магазина совпадает с API; поиск находит книгу; неизвестный запрос даёт пустой результат. |
| test_profile_books.py | Пустой профиль, вход для гостя, список книг, добавление одной и трёх книг, отказ при дубле, удаление одной и всех книг, отмена обоих видов удаления. |
| test_e2e.py | Вход через UI, переход в магазин, добавление трёх книг, удаление одной через UI и проверка оставшихся книг через API и UI. |

## Структура

- conftest.py — параметры pytest, фикстуры браузера, API и временного пользователя, скриншот при падении UI-теста.
- pages/base_page.py — открытие URL, явные ожидания и обычный клик с прокруткой к элементу.
- pages/login_page.py, pages/book_store_page.py, pages/book_detail_page.py, pages/profile_page.py — действия на страницах.
- swagger/client.py — простой HTTP-клиент с шагами Allure и таймаутом.
- swagger/schemas.py — JSON-схемы ответов API.
- tests/ui/ — UI и end-to-end тесты.
- tests/api/ — API-тесты.
- pytest.ini — маркеры и путь для результатов Allure.
- requirements.txt — зафиксированные Python-зависимости.

## Отчёты Allure

После запуска pytest результаты находятся в allure-results. Следующий запуск очищает старые результаты, поэтому отчёт соответствует последнему прогону. Чтобы видеть вместе UI и API, запускайте весь набор одной командой.

    allure serve allure-results

Для сохранения HTML-отчёта:

    allure generate allure-results --clean -o allure-report

В отчёте есть названия тестов, шаги, статусы и вложения. При падении UI-теста после открытия браузера автоматически сохраняется PNG-скриншот. Если браузер не запустился, снять скриншот невозможно. Каталоги отчётов исключены из Git.

## Замечания

После подтверждения удаления всех книг DemoQA иногда оставляет окно подтверждения открытым. Page Object ждёт завершения запроса и обновляет профиль перед проверкой. При добавлении набора, содержащего уже имеющийся ISBN, DemoQA может ответить HTTP 201; поэтому негативный сценарий для набора проверяет отсутствие авторизации. DemoQA — внешний учебный сервис. Его данные, разметка и ответы могут измениться. UI-тесты используют явные ожидания, без фиксированных пауз. Для тестов с созданием аккаунта нужен доступ к API даже при запуске только UI-набора. Если тест оборвётся до очистки аккаунта из-за остановки процесса, временный пользователь может остаться на сервисе.
