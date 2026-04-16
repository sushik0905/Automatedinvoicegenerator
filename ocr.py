# ocr.py

import pytesseract
import cv2
import re

# ✅ Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# ✅ OCR FUNCTION (IMPROVED)
# =========================
def extract_text(file_path):
    image = cv2.imread(file_path)

    # Resize (better OCR)
    image = cv2.resize(image, None, fx=2, fy=2)

    # Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise removal
    gray = cv2.medianBlur(gray, 3)

    # Threshold
    gray = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # OCR config (table-like data)
    custom_config = r'--oem 3 --psm 4'

    text = pytesseract.image_to_string(gray, config=custom_config)

    return text


# =========================
# ✅ PARSER (HIGHLY STABLE)
# =========================
def parse_invoice_data(text):
    data = {
        "customer": "Unknown",
        "date": "Unknown",
        "invoice_no": "INV001",
        "items": [],
        "total": "0"
    }

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # =========================
    # ✅ HEADER EXTRACTION
    # =========================
    for line in lines:
        lower = line.lower()

        if "invoice" in lower and len(line) < 50:
            data["invoice_no"] = line

        elif "date" in lower:
            data["date"] = line

        elif "bill to" in lower or "customer" in lower:
            data["customer"] = line

    # =========================
    # ✅ ITEM EXTRACTION (STRICT)
    # =========================
    items = []

    for line in lines:

        # 🔥 Pattern 1: Product 2 50 100
        match_full = re.search(r"(.+?)\s+(\d+)\s+(\d+)\s+(\d+)", line)

        if match_full:
            name = match_full.group(1).strip()
            qty = int(match_full.group(2))
            price = int(match_full.group(3))
            total = int(match_full.group(4))

        else:
            # 🔥 Pattern 2: Product 2 50
            match_simple = re.search(r"(.+?)\s+(\d+)\s+(\d+)", line)

            if match_simple:
                name = match_simple.group(1).strip()
                qty = int(match_simple.group(2))
                price = int(match_simple.group(3))
                total = qty * price
            else:
                continue

        # 🚫 FILTER GARBAGE LINES
        skip_words = [
            "invoice", "date", "total", "tax", "gst",
            "amount", "bill", "balance", "cgst", "sgst"
        ]

        if any(word in name.lower() for word in skip_words):
            continue

        # 🚫 Ignore numeric-only or weird lines
        if len(name) < 3 or name.isdigit():
            continue

        # 🚫 Avoid very large numbers (totals misread)
        if qty > 1000 or price > 100000:
            continue

        items.append({
            "name": name,
            "quantity": qty,
            "price": price,
            "total": total
        })

    # =========================
    # ✅ REMOVE DUPLICATES
    # =========================
    unique_items = []
    seen = set()

    for item in items:
        key = (item["name"], item["quantity"], item["price"])
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    data["items"] = unique_items

    # =========================
    # ✅ TOTAL
    # =========================
    total_amount = sum(item["total"] for item in data["items"])
    data["total"] = str(total_amount)

    return data