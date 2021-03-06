from fastapi.testclient import TestClient
from app.main import UPLOAD_DIR, Settings, app, BASE_DIR, get_settings
import shutil
import time
from PIL import Image, ImageChops
import io

client = TestClient(app) # r = requests.get(...)

def test_get_home():
    response = client.get("/") # r = requests.get #python request
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "text/html" in response.headers["content-type"]
    assert b"h1>Code On! 123</h1>" in response.content
    assert response.text != "<h1>Hello World</h1>"

def test_invalid_file_upload_error():
    response = client.post("/") # r = requests.post #python request
    assert response.status_code == 422
    assert "application/json" in response.headers["content-type"]

def test_prediction_upload_missing_header():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/", 
                        files={"file": open(path, 'rb')}) # r = requests.post #python request

        assert response.status_code == 401

def test_prediction_upload():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/", 
                        headers={"Authorization": f"JWT {settings.app_auth_token}"},
                        files={"file": open(path, 'rb')}) # r = requests.post #python request
        if img is None:
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            r_steam = io.BytesIO(response.content)
            data = response.json()
            assert len(data.keys()) == 2

    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)

valid_image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
def test_echo_upload():
    img_saved_path = BASE_DIR / "images"
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/img-echo/", files={"file": open(path, 'rb')}) # r = requests.post #python request
        if img is None:
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            r_steam = io.BytesIO(response.content)
            echo_img = Image.open(r_steam)

            #assert img.size == echo_img.size
            difference = ImageChops.difference(img, echo_img).getbbox()
            assert difference is None

    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)