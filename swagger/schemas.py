BOOK_SCHEMA = {
    "type": "object",
    "required": ["isbn", "title", "author"],
    "properties": {
        "isbn": {"type": "string"},
        "title": {"type": "string"},
        "author": {"type": "string"},
    },
}

CATALOG_SCHEMA = {
    "type": "object",
    "required": ["books"],
    "properties": {"books": {"type": "array", "items": BOOK_SCHEMA}},
}

PROFILE_SCHEMA = {
    "type": "object",
    "required": ["userId", "username", "books"],
    "properties": {
        "userId": {"type": "string"},
        "username": {"type": "string"},
        "books": {"type": "array", "items": BOOK_SCHEMA},
    },
}

ADDED_BOOKS_SCHEMA = {
    "type": "object",
    "required": ["books"],
    "properties": {
        "books": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["isbn"],
                "properties": {"isbn": {"type": "string"}},
            },
        }
    },
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["code", "message"],
    "properties": {
        "code": {"type": ["string", "integer"]},
        "message": {"type": "string"},
    },
}
