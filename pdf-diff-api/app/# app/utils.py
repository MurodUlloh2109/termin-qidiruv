# app/utils.py
from pdf2image import convert_from_bytes
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from PIL import Image
from typing import List

def pdf_to_images(pdf_bytes: bytes) -> List[np.ndarray]:
    """PDFni sahifalarga bo‘lib, RGB NumPy massivlarga aylantiradi"""
    try:
        images = convert_from_bytes(pdf_bytes, dpi=200)
        return [np.array(img.convert("RGB")) for img in images]
    except Exception as e:
        raise ValueError(f"PDFni rasmga aylantirishda xato: {e}")

def resize_image(img: np.ndarray, width: int, height: int) -> np.ndarray:
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

def compare_two_images(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Ikki rasmni taqqoslab, farqni qizil bilan belgilaydi"""
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    height, width = min(h1, h2), min(w1, w2)

    img1_resized = resize_image(img1, width, height)
    img2_resized = resize_image(img2, width, height)

    gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_RGB2GRAY)

    score, diff = ssim(gray1, gray2, full=True)
    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY_INV)[1]

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img2_resized.copy()
    cv2.drawContours(result, contours, -1, (0, 0, 255), 2)  # Qizil chiziq

    # SSIM skorini rasmga yozish
    cv2.putText(result, f"SSIM: {score:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return result
