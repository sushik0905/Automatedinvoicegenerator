# invoice_generator.py

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def calculate_total(items, tax_percent=0):
    subtotal = sum(item["quantity"] * item["price"] for item in items)
    tax = subtotal * (tax_percent / 100)
    total = subtotal + tax
    return subtotal, tax, total


def generate_invoice(data, file_path):
    styles = getSampleStyleSheet()
    elements = []

    doc = SimpleDocTemplate(file_path)

    # ✅ SAFE DATA EXTRACTION (no crash)
    company_name = data.get("company", {}).get("name", "My Company")
    company_address = data.get("company", {}).get("address", "Address not available")
    company_phone = data.get("company", {}).get("phone", "Phone not available")

    customer_name = data.get("customer", "Unknown Customer")
    invoice_number = data.get("invoice_no", "INV-001")
    date = data.get("date", "N/A")
    items = data.get("items", [])
    tax_percent = data.get("tax_percent", 0)

    # Title
    elements.append(Paragraph("INVOICE", styles['Title']))
    elements.append(Spacer(1, 10))

    # Company Info
    elements.append(Paragraph(f"<b>{company_name}</b>", styles['Normal']))
    elements.append(Paragraph(company_address, styles['Normal']))
    elements.append(Paragraph(company_phone, styles['Normal']))
    elements.append(Spacer(1, 10))

    # Customer Info
    elements.append(Paragraph(f"<b>Bill To:</b> {customer_name}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # Invoice Info
    elements.append(Paragraph(f"Invoice No: {invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"Date: {date}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Table Header
    table_data = [["Item", "Qty", "Price", "Total"]]

    # Items
    for item in items:
        total_price = item["quantity"] * item["price"]
        table_data.append([
            item["name"],
            item["quantity"],
            f"₹{item['price']}",
            f"₹{total_price}"
        ])

    # Totals
    subtotal, tax, total = calculate_total(items, tax_percent)

    table_data.append(["", "", "Subtotal", f"₹{subtotal}"])
    table_data.append(["", "", f"Tax ({tax_percent}%)", f"₹{tax}"])
    table_data.append(["", "", "Total", f"₹{total}"])

    # Table Styling
    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey)
    ]))

    elements.append(table)

    doc.build(elements)
