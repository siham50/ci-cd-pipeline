import os
import sys
import pytest

# Ensure the app directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

import app as app_module  # noqa: E402
from app import app  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_state():
    app_module.tasks.clear()
    app_module.task_id_counter = 1
    yield
    app_module.tasks.clear()
    app_module.task_id_counter = 1


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Test Task"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["title"] == "Test Task"
    assert data["done"] is False


def test_create_task_missing_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_create_task_empty_title(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Title is required"}


def test_get_task_by_id(client):
    client.post("/tasks", json={"title": "Specific Task"})
    response = client.get("/tasks/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert data["title"] == "Specific Task"


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Task not found"}


def test_update_task(client):
    client.post("/tasks", json={"title": "Initial Task"})
    response = client.put(
        "/tasks/1",
        json={"title": "Updated Task", "done": True}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Task"
    assert data["done"] is True


def test_update_task_not_found(client):
    response = client.put("/tasks/999", json={"title": "Ghost Task"})
    assert response.status_code == 404
    assert response.get_json() == {"error": "Task not found"}


def test_delete_task(client):
    client.post("/tasks", json={"title": "Task to Delete"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.get_json() == {"message": "Task deleted"}

    # Verify task is no longer present
    get_response = client.get("/tasks/1")
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Task not found"}
