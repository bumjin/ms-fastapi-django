from fastapi.testclient import TestClient
from app.main import UPLOAD_DIR, app, BASE_DIR
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

def test_post_home_detail_view():
    response = client.post("/") # r = requests.post #python request
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert response.json() == {"hello": "World"}

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

    #time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)