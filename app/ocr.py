import pathlib
import pytesseract
from PIL import Image

BASE_DIR = pathlib.Path(__file__).parent
IMG_DIR = BASE_DIR / 'images'
#img_path = IMG_DIR / 'ingredients-1.png'
img_path = IMG_DIR / 'kor3.png'
#print(img_path)
img = Image.open(img_path)

preds = pytesseract.image_to_string(img,lang='kor')
#preds = pytesseract.image_to_string(img,lang='kor+eng')
predictions = [x for x in preds.split('\n')]
#print(preds)
print(predictions)