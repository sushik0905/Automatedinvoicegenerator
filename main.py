# main.py

import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from ocr import extract_text, parse_invoice_data
from invoice_generator import generate_invoice

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# ✅ Home Page
@app.get("/", response_class=HTMLResponse)
def home():
    with open(os.path.join(BASE_DIR, "templates", "index.html"), "r", encoding="utf-8") as f:
        return f.read()


# ✅ Upload + Preview
@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):

    upload_dir = os.path.join(BASE_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ✅ OCR
    text = extract_text(file_path)

    # 🔥 DEBUG (IMPORTANT)
    print("\n========== OCR TEXT ==========")
    print(text)
    print("================================\n")

    # ✅ Parse data
    data = parse_invoice_data(text)

    print("\n========== PARSED DATA ==========")
    print(data)
    print("================================\n")

    # ✅ Generate PDF
    invoice_dir = os.path.join(BASE_DIR, "invoices")
    os.makedirs(invoice_dir, exist_ok=True)

    invoice_path = os.path.join(invoice_dir, "ocr_invoice.pdf")
    generate_invoice(data, invoice_path)

    # ✅ If no items detected → show message
    if not data.get("items"):
        items_html = "<tr><td colspan='4'>⚠️ No items detected. Try clearer image.</td></tr>"
    else:
        items_html = ""
        for item in data["items"]:
            items_html += f"""
            <tr>
                <td>{item['name']}</td>
                <td>{item['quantity']}</td>
                <td>{item['price']}</td>
                <td>{item['total']}</td>
            </tr>
            """

    # ✅ HTML Preview
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
          <title>Invoice Result</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

<div class="background"></div>

<div class="container glass">

    <h1>📄 Extracted Invoice</h1>

    <p><strong>Invoice No:</strong> {data.get("invoice_no")}</p>
    <p><strong>Date:</strong> {data.get("date")}</p>
    <p><strong>Customer:</strong> {data.get("customer")}</p>

    <table>
        <tr>
            <th>Product</th>
            <th>Qty</th>
            <th>Price</th>
            <th>Total</th>
        </tr>
        {items_html}
    </table>

    <h2>💰 Total: ₹{data.get("total")}</h2>

    <a href="/download">
        <button>⬇ Download PDF</button>
    </a>

    <br>

    <a href="/">
        <button>⬅ Back</button>
        </a>
    </div>

    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


# ✅ Download Route
@app.get("/download")
def download_invoice():
    invoice_path = os.path.join(BASE_DIR, "invoices", "ocr_invoice.pdf")
    return FileResponse(invoice_path, media_type="application/pdf", filename="invoice.pdf")
