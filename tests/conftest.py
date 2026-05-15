import os
import tempfile
import subprocess

import pytest
from task_manager import create_app
from task_manager.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()

        # run dbmate against the temp test database
        subprocess.run(
            ["dbmate", "--url", f"sqlite:{db_path}", "--no-dump-schema", "up"],
            check=True
        )

        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            json={'username': username, 'password': password}
        )


@pytest.fixture
def auth(client):
    return AuthActions(client)
