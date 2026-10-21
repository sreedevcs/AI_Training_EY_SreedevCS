from fastapi.testclient import TestClient
from main import app
client=TestClient(app)

def test_get_products():
    # Act
    response=client.get("/products")
    # Assert
    assert response.status_code==200

def test_add_product():
    response = client.post(
        "/products",
        json={
            "id": 101,
            "name": "Webcam",
            "price": 3200
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 101
    assert data["name"] == "Webcam"
    assert data["price"] == 3200