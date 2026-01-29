import pytesseract
from PIL import Image
import io

async def extract_text_from_image(file):
    img_bytes = await file.read()
    img = Image.open(io.BytesIO(img_bytes))
    text = pytesseract.image_to_string(img)
    return text.strip()