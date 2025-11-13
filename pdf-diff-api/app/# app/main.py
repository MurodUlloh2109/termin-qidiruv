# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils import pdf_to_images, compare_two_images
from io import BytesIO
from PIL import Image
import logging

app = FastAPI(
    title="PDF Diff API",
    description="Ikkita PDFni taqqoslab, farqlarni qizil bilan belgilaydi",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app/templates")
logging.basicConfig(level=logging.INFO)

def images_to_stream(images: list) -> BytesIO:
    buf = BytesIO()
    for i, img in enumerate(images):
        pil_img = Image.fromarray(img)
        pil_img.save(buf, format="PNG")
        if i < len(images) - 1:
            buf.write(b"\n--frame\n")
    buf.seek(0)
    return buf

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/compare-pdf")
async def compare_pdf(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    if file1.content_type != "application/pdf" or file2.content_type != "application/pdf":
        raise HTTPException(400, "Ikkala fayl ham PDF bo‘lishi kerak!")

    pdf1_bytes = await file1.read()
    pdf2_bytes = await file2.read()

    try:
        images1 = pdf_to_images(pdf1_bytes)
        images2 = pdf_to_images(pdf2_bytes)
    except Exception as e:
        raise HTTPException(500, f"PDFni ochishda xato: {e}")

    if len(images1) == 0 or len(images2) == 0:
        raise HTTPException(400, "PDFda sahifa topilmadi")

    # Faqat umumiy sahifalarni taqqoslaymiz
    min_pages = min(len(images1), len(images2))
    diff_images = []
    for i in range(min_pages):
        diff = compare_two_images(images1[i], images2[i])
        diff_images.append(diff)

    # Agar sahifalar soni farq qilsa
    if len(images1) > min_pages:
        for img in images1[min_pages:]:
            diff_images.append(img)  # Qo‘shimcha sahifalar
    elif len(images2) > min_pages:
        for img in images2[min_pages:]:
            diff_images.append(img)

    buffer = images_to_stream(diff_images)
    return StreamingResponse(
        buffer,
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Content-Disposition": "attachment; filename=diff_result.png"}
    )
