from query_processor import QueryProcessor


def test_where_gte_operator_filters_correctly():
    processor = QueryProcessor()
    processor.process("CREATE TABLE users(id, age);")
    processor.process("INSERT INTO users(id, age) VALUES (1, 29);")
    processor.process("INSERT INTO users(id, age) VALUES (2, 30);")

    result = processor.process("SELECT * FROM users WHERE age >= 30;")

    assert result == {"data": [{"id": 2, "age": 30}]}


def test_where_lte_operator_filters_correctly():
    processor = QueryProcessor()
    processor.process("CREATE TABLE users(id, age);")
    processor.process("INSERT INTO users(id, age) VALUES (1, 29);")
    processor.process("INSERT INTO users(id, age) VALUES (2, 30);")

    result = processor.process("SELECT * FROM users WHERE age <= 29;")

    assert result == {"data": [{"id": 1, "age": 29}]}
