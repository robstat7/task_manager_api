import pytest
from flask import g, session
from task_manager.db import get_db
import json


def test_register(client, app):
    response = client.post(
        '/auth/register', json={'username': 'a', 'password': 'a'}
    )

    response_dict = json.loads(response.get_data(as_text=True))

    assert response_dict["message"] == "user registered successfully"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', 'Username is required.'),
    ('a', '', 'Password is required.'),
    ('test', 'test', 'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        json={'username': username, 'password': password}
    )

    response_dict = json.loads(response.get_data(as_text=True))

    assert message in response_dict["error"]


def test_login(client, auth):
    response = auth.login()

    response_dict = json.loads(response.get_data(as_text=True))

    assert response_dict["message"] == "login success"


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', 'Incorrect username.'),
    ('test', 'a', 'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)

    response_dict = json.loads(response.get_data(as_text=True))
    assert message in response_dict["error"]
