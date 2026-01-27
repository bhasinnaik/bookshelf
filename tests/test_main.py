from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI"}

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_item():
    """Test get item endpoint."""
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "name": "Item 42"}

def test_create_item():
    """Test create item endpoint."""
    response = client.post("/items/?name=Test&description=A test item")
    assert response.status_code == 200
    assert response.json() == {"name": "Test", "description": "A test item"}
