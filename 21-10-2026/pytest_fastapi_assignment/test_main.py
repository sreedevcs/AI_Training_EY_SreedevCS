from fastapi.testclient import TestClient
from main import app
client=TestClient(app)

def test_get_tasks():
    # Act
    response=client.get("/tasks")
    # Assert
    assert response.status_code==200
def test_get_task_type():
    response=client.get("/tasks")
    assert isinstance(response.json(),list)

def test_get_task_by_id():
    response=client.get("/tasks/1")
    assert response.status_code==200 and response.json()["id"]==1

def test_get_task_not_exists():
    response=client.get("/tasks/999")
    assert response.status_code==404


def test_add_tasks():
    response = client.post(
        "/tasks",
        json={
            "id": 4,
            "title": "Check server logs",
            "status": "Pending"
        }
    )

    assert response.status_code==200
    data=response.json()["task"]

    assert data["id"]==4
    assert data["title"]=="Check server logs"
    assert data["status"]=="Pending"

def test_add_tasks_missing_value():
    response = client.post(
        "/tasks",
        json={
            "id": 5,
            "status": "Pending"
        }
    )
    assert response.status_code==422

def test_update_task():
    response=client.put(
        "/tasks/2",
        json={
            "id":2,
            "title":"Review invoice",
            "status":"Completed"
        }
    )
    assert response.status_code==200
    assert response.json()["status"]=="Completed"

def test_delete_task():
    response=client.delete("/tasks/3")
    assert response.status_code==200

def test_check_task_not_exists():
    client.delete("/tasks/3")
    response=client.get("/tasks/3")
    assert response.status_code==404