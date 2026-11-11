## Требования и установка
Из корня проекта:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt


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

## Параметры окружения

- DEMOQA_BASE_URL — адрес UI
- DEMOQA_API_BASE_URL — адрес API
- DEMOQA_UI_WAIT_SECONDS — время явного ожидания элементов
- DEMOQA_API_TIMEOUT_SECONDS — таймаут HTTP-запроса,

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
| test_add_unknown_book | Неизвестный ISBN отклоняется, профиль остаётся пустым. |
| test_add_batch_without_authorization | Без токена добавление нескольких книг запрещено, профиль пуст. |
| test_delete_one_book | Удаляется одна книга, другая остаётся. |
| test_delete_missing_book | Удаление отсутствующей книги возвращает HTTP 400. |
| test_delete_multiple_books | Удаляются все три книги, профиль пустеет. |
| test_delete_without_authorization | Без токена удаление запрещено, книга остаётся. |
| test_delete_all_without_authorization | Без токена удаление всех книг запрещено, обе остаются. |


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

В отчёте есть названия тестов, шаги, статусы и вложения. При падении UI-теста после открытия браузера автоматически сохраняется PNG-скриншот
