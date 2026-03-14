from app import app


def test_invalid_query_returns_bad_request_when_authenticated():
    app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)

    with app.test_client() as client:
        login_response = client.post(
            "/login", json={"username": "admin", "password": "password"}
        )
        assert login_response.status_code == 200

        response = client.post("/query", json={"query": "BOGUS"})

        assert response.status_code == 400
        assert response.get_json() == {"error": "Unsupported command: BOGUS"}
