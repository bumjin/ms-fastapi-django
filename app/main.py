import pathlib
import os
import io
import uuid
from functools import lru_cache
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Depends,
    Request,
    File,
    UploadFile
    )
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from PIL import Image
import pytesseract

class Settings(BaseSettings):
    debug: bool = False
    echo_active: bool = False
    app_auth_token: str = None
    app_auth_token_prod: str = None
    skip_auth: bool = False
    class Config:
        env_file = '.env'

@lru_cache
def get_settings():
    return Settings()

settins=get_settings()
DEBUG=settins.debug
BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / 'uploaded'

# print((BASE_DIR / "templates").exists())

app = FastAPI()
templats = Jinja2Templates(directory=BASE_DIR/'templates')
#print('DEBUG:', DEBUG)
# REST API

@app.get("/", response_class=HTMLResponse) # http GET -> JSON
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    print(settings.debug)
    return templats.TemplateResponse('home.html', {'request': request, "abc": "123"})


def verify_auth(authorization = Header(None), settings: Settings = Depends(get_settings)):
    """
    Authorization: Bearrerer <token>
    {"authorization": "Bearrerer <token>"}
    """
    print(settings.dict())
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(status_code=401, detail="Invalid endpoint")

    label, token = authorization.split()
    #print('token', token)
    #print('settings.app_auth_token', settings.app_auth_token)
    if token != settings.app_auth_token:
        raise HTTPException(status_code=401, detail="Invalid endpoint")

@app.post("/") # http POST
async def prediction_view(file:UploadFile = File(...), authorization=Header(None), settings: Settings = Depends(get_settings)):
    verify_auth(authorization, settings)
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid image")

    preds = pytesseract.image_to_string(img,lang='kor+eng')
    predictions = [x for x in preds.split('\n')]

    return {"result:": predictions, "original": preds}

@app.post("/img-echo/", response_class=FileResponse) # http POST
async def img_echo_view(file:UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(status_code=400, detail="Invalid endpoint")
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid image")
    fname = pathlib.Path(file.filename)
    fext = fname.suffix #.jpg #.png
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    img.save(dest)

    return dest