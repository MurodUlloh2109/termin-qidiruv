from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "<h1>PDF Fayllarni Taqqoslash</h1>" in response.text

def test_compare_pdf_invalid_file():
    response = client.post("/compare-pdf", files={
        "file1": ("test.txt", b"not a pdf", "text/plain"),
        "file2": ("test.txt", b"not a pdf", "text/plain")
    })
    assert response.status_code == 400
    assert "Ikkala fayl ham PDF bo‘lishi kerak" in response.json()["detail"]

# Haqiqiy PDF testlari uchun kichik PDF kerak bo‘ladi
