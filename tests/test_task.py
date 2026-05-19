import pytest
import json
from task_manager.db import get_db

def test_index(client, auth):
    response = client.get('/api/tasks')
    assert b"Missing Authorization Header" in response.data

    login_response = auth.login()

    login_response_dict = json.loads(login_response.get_data(as_text=True))
    token = login_response_dict["access_token"]
    
    response = client.get(
        "/api/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    get_response_list = json.loads(response.get_data(as_text=True))

    assert get_response_list[0]["task_id"] == 1
    assert get_response_list[0]["task_title"] == "test title"
    assert get_response_list[0]["task_description"] == "test"
    assert get_response_list[0]["task_category"] == "work"
    assert get_response_list[0]["task_status"] == "pending"


have_patched_task_1 = False

@pytest.mark.parametrize('path', (
    '/api/tasks',
    '/api/tasks/1',
    '/api/tasks/1',
    '/api/tasks/1/status',
    '/api/tasks/1/category',
))
def test_login_required(client, path):
    response = None

    if path == '/api/tasks':
        response = client.post(path)
    else:
        global have_patched_task_1
        if path == '/api/tasks/1' and have_patched_task_1:
            response = client.delete(path)
        else:
            response = client.patch(path)
            if path == '/api/tasks/1':
                have_patched_task_1 = True

    assert b"Missing Authorization Header" in response.data


def test_author_required(app, client, auth):
    # change the task author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE task SET user_id = 2 WHERE id = 1')
        db.commit()

    login_response = auth.login()

    login_response_dict = json.loads(login_response.get_data(as_text=True))
    token = login_response_dict["access_token"]
     
    # current user can't modify other user's task 

    assert client.patch(
        "/api/tasks/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    ).status_code == 403

    assert client.delete(
        "/api/tasks/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    ).status_code == 403


def test_exists_required(client, auth):
    login_response = auth.login()

    login_response_dict = json.loads(login_response.get_data(as_text=True))
    token = login_response_dict["access_token"]
     
    assert client.patch(
        "/api/tasks/2",
        headers={
            "Authorization": f"Bearer {token}"
        }
    ).status_code == 404

    assert client.delete(
        "/api/tasks/2",
        headers={
            "Authorization": f"Bearer {token}"
        }
    ).status_code == 404
