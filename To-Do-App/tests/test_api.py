import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Task


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


# ====== User Tests ======

def test_create_user_success(client):
    response = client.post('/api/users', json={
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["full_name"] == "Test User"


def test_create_user_missing_fields(client):
    response = client.post('/api/users', json={
        "full_name": "",
        "email": "testuser2@example.com",
        "password": ""
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data



def test_create_user_existing_email(client):
    client.post('/api/users', json={
        "full_name": "Exist User",
        "email": "exist@example.com",
        "password": "password"
    })
    response = client.post('/api/users', json={
        "full_name": "Exist User2",
        "email": "exist@example.com",
        "password": "password"
    })
    assert response.status_code == 409
    data = response.get_json()
    assert "error" in data


def test_create_user_missing_email(client):
    response = client.post('/api/users', json={
        "full_name": "No Email",
        "password": "password"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_user_missing_full_name(client):
    response = client.post('/api/users', json={
        "email": "nofullname@example.com",
        "password": "password"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_login_user_success(client):
    client.post('/api/users', json={
        "full_name": "Login User",
        "email": "login@example.com",
        "password": "password"
    })
    response = client.post('/api/login', json={
        "email": "login@example.com",
        "password": "password"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Login successful"


def test_login_user_invalid_password(client):
    client.post('/api/users', json={
        "full_name": "Wrong Password User",
        "email": "wrongpass@example.com",
        "password": "password"
    })
    response = client.post('/api/login', json={
        "email": "wrongpass@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_login_user_missing_password(client):
    response = client.post('/api/login', json={"email": "user@example.com"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_login_user_missing_email(client):
    response = client.post('/api/login', json={"password": "password"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_login_user_missing_email_and_password(client):
    response = client.post('/api/login', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


# ====== Task Tests ======

def test_create_task_success(client):
    client.post('/api/users', json={
        "full_name": "Task User",
        "email": "taskuser@example.com",
        "password": "password"
    })
    client.post('/api/login', json={
        "email": "taskuser@example.com",
        "password": "password"
    })
    response = client.post('/api/tasks', json={"title": "New Task"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "New Task"


def test_create_task_missing_title(client):
    client.post('/api/users', json={
        "full_name": "Task User2",
        "email": "taskuser2@example.com",
        "password": "password"
    })
    client.post('/api/login', json={
        "email": "taskuser2@example.com",
        "password": "password"
    })
    response = client.post('/api/tasks', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_task_missing_user_id_in_session(client):
    with client.session_transaction() as sess:
        sess.clear()
    response = client.post('/api/tasks', json={"title": "Test"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_get_tasks(client):
    client.post('/api/users', json={
        "full_name": "Get Task User",
        "email": "gettask@example.com",
        "password": "password"
    })
    client.post('/api/login', json={
        "email": "gettask@example.com",
        "password": "password"
    })
    client.post('/api/tasks', json={"title": "Task 1"})
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(task["title"] == "Task 1" for task in data)


def test_update_task(client):
    client.post('/api/users', json={
        "full_name": "Update User",
        "email": "updateuser@example.com",
        "password": "password"
    })
    client.post('/api/login', json={
        "email": "updateuser@example.com",
        "password": "password"
    })
    res = client.post('/api/tasks', json={"title": "Old Title"})
    task_id = res.get_json()["id"]
    response = client.put(f'/api/tasks/{task_id}', json={
        "title": "New Title",
        "is_done": True
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "New Title"
    assert data["is_done"] is True


def test_update_task_partial_fields(client):
    client.post('/api/users', json={
        "full_name": "Partial Update User",
        "email": "partial@example.com",
        "password": "password"
    })
    client.post('/api/login', json={
        "email": "partial@example.com",
        "password": "password"
    })
    res = client.post('/api/tasks', json={"title": "Initial Title"})
    task_id = res.get_json()["id"]
    response = client.put(f'/api/tasks/{task_id}', json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Title"


def test_delete_task(client):
    client.post('/api/users', json={
        "full_name": "Delete User",
        "email": "deleteuser@example.com",
        "password": "password"
    })
    client.post('/api/login', json={
        "email": "deleteuser@example.com",
        "password": "password"
    })
    res = client.post('/api/tasks', json={"title": "Task to delete"})
    task_id = res.get_json()["id"]
    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data


# ====== Negative/Error Tests ======

def test_get_user_not_found(client):
    response = client.get('/api/users/9999')
    assert response.status_code == 404


def test_get_task_not_found(client):
    response = client.get('/api/tasks/9999')
    assert response.status_code == 404


def test_update_task_not_found(client):
    response = client.put('/api/tasks/9999', json={"title": "Test"})
    assert response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete('/api/tasks/9999')
    assert response.status_code == 404


def test_get_user_not_found(client):
    response = client.get('/api/users/9999')  # Non-existent user ID
    assert response.status_code == 404

def test_get_task_not_found(client):
    response = client.get('/api/tasks/9999')  # Non-existent task ID
    assert response.status_code == 404

def test_update_task_not_found(client):
    response = client.put('/api/tasks/9999', json={"title": "Test"})
    assert response.status_code == 404

def test_delete_task_not_found(client):
    response = client.delete('/api/tasks/9999')
    assert response.status_code == 404


@pytest.fixture
def login_session(client):
    # Create user in db first
    with app.app_context():
        if not User.query.filter_by(email="testuser@example.com").first():
            user = User(full_name="Test User", email="testuser@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
    with client.session_transaction() as sess:
        user = User.query.filter_by(email="testuser@example.com").first()
        sess['user_id'] = user.id
        sess['user_name'] = user.full_name
    yield



def test_login_missing_email(client):
    res = client.post("/api/login", json={"password": "somepass"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Missing email or password"

def test_login_missing_password(client):
    res = client.post("/api/login", json={"email": "user@example.com"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Missing email or password"


def test_login_wrong_email(client):
    res = client.post("/api/login", json={"email": "wrong@example.com", "password": "pass"})
    assert res.status_code == 401

def test_login_wrong_password(client, test_user):
    res = client.post("/api/login", json={"email": test_user["email"], "password": "wrongpass"})
    assert res.status_code == 401

def test_get_user_not_found(client):
    res = client.get("/api/users/99999")
    assert res.status_code == 404


@pytest.fixture
def test_user(client):
    user_data = {
        "full_name": "Fixture User",
        "email": "fixture@example.com",
        "password": "test123"
    }
    client.post("/api/users", json=user_data)
    return user_data


def test_get_users(client):
    # Optional: create a user first if your DB is empty
    client.post('/api/users', json={
        "full_name": "Test User",
        "email": "getuser@example.com",
        "password": "password123"
    })

    response = client.get('/api/users')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(user['email'] == 'getuser@example.com' for user in data)



def test_get_existing_user(client):
    # First, create a user
    response = client.post('/api/users', json={
        "full_name": "Sample User",
        "email": "sampleuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    user_id = response.get_json()["id"]

    # Now, get the created user
    response = client.get(f'/api/users/{user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["full_name"] == "Sample User"
    assert data["email"] == "sampleuser@example.com"



def test_get_existing_task(client):
    # Create user
    user_resp = client.post('/api/users', json={
        "full_name": "Task Owner",
        "email": "taskowner@example.com",
        "password": "pass123"
    })
    assert user_resp.status_code == 201
    user_id = user_resp.get_json()["id"]

    # Create task (without description)
    task_resp = client.post('/api/tasks', json={
        "title": "Test Task",
        "user_id": user_id
    })
    assert task_resp.status_code == 201
    task_id = task_resp.get_json()["id"]

    # Fetch task
    get_resp = client.get(f'/api/tasks/{task_id}')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data["title"] == "Test Task"
