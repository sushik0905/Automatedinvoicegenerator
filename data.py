# data.py

invoice_data = {
    "invoice_number": "INV-2026-001",
    "date": "2026-04-15",

    "company": {
        "name": "ABC Technologies Pvt Ltd",
        "address": "Hyderabad, India",
        "phone": "+91 9876543210"
    },

    "customer": {
        "name": "John Doe",
        "address": "Bangalore, India"
    },

    "items": [
        {"name": "Laptop", "quantity": 1, "price": 55000},
        {"name": "Mouse", "quantity": 2, "price": 500},
        {"name": "Keyboard", "quantity": 1, "price": 2000}
    ],

    "tax_percent": 18
}
