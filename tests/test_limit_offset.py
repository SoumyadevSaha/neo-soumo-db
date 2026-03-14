from query_processor import QueryProcessor


def _seed_users():
    processor = QueryProcessor()
    processor.process("CREATE TABLE users(id, age);")
    processor.process("INSERT INTO users(id, age) VALUES (1, 21);")
    processor.process("INSERT INTO users(id, age) VALUES (2, 22);")
    return processor


def test_limit_zero_returns_no_rows():
    processor = _seed_users()

    result = processor.process("SELECT * FROM users LIMIT 0;")

    assert result == {"data": []}


def test_offset_zero_still_applies_limit():
    processor = _seed_users()

    result = processor.process("SELECT * FROM users LIMIT 1 OFFSET 0;")

    assert result == {"data": [{"id": 1, "age": 21}]}
