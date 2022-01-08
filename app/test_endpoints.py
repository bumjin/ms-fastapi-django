from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app) # r = requests.get(...)

def test_get_home():
    response = client.get("/") # r = requests.get #python request
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "text/html" in response.headers["content-type"]
    assert b"h1>Code On! 123</h1>" in response.content
    assert response.text != "<h1>Hello World</h1>"

def test_post_home_detail_view():
    response = client.post("/") # r = requests.post #python request
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert response.json() == {"hello": "World"}
