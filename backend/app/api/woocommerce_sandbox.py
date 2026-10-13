from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime
import copy

sandbox_router = APIRouter(prefix="/wp-json/wc/v3", tags=["WooCommerce Store Sandbox API"])

# India-Specific E-Commerce Products (in INR ₹)
SEEDED_PRODUCTS = [
    {"id": 101, "name": "boAt Rockerz 550 Wireless Over-Ear Headphones", "price": "1999.00", "sku": "BOAT-ROC-550", "stock_status": "instock"},
    {"id": 102, "name": "Keychron K2 Wireless Mechanical Keyboard (RGB)", "price": "8499.00", "sku": "KEY-K2-RGB", "stock_status": "instock"},
    {"id": 103, "name": "OnePlus 32-inch Y Series HD Android TV", "price": "14999.00", "sku": "1PLUS-TV-32Y", "stock_status": "instock"},
    {"id": 104, "name": "Logitech MX Master 3S Wireless Mouse", "price": "9495.00", "sku": "LOGI-MX3S-IN", "stock_status": "instock"},
    {"id": 105, "name": "Noise ColorFit Pulse 3 Smartwatch (AMOLED)", "price": "2499.00", "sku": "NOISE-CF-P3", "stock_status": "instock"},
    {"id": 106, "name": "Wipro 16A Smart Wi-Fi Plug with Energy Monitor", "price": "999.00", "sku": "WIPRO-16A-SP", "stock_status": "instock"},
]

# India-Specific Customers with Authentic Names & Addresses
SEEDED_CUSTOMERS = [
    {
        "id": 1,
        "date_created": "2026-01-15T10:20:30",
        "email": "aarav.sharma@gmail.com",
        "first_name": "Aarav",
        "last_name": "Sharma",
        "role": "customer",
        "username": "aaravs",
        "billing": {
            "first_name": "Aarav", "last_name": "Sharma", "company": "Infosys BPM",
            "address_1": "Flat 402, Prestige Shantiniketan, Whitefield", "city": "Bengaluru", "state": "KA",
            "postcode": "560048", "country": "IN", "email": "aarav.sharma@gmail.com", "phone": "+91 98450 12345"
        },
        "shipping": {
            "first_name": "Aarav", "last_name": "Sharma",
            "address_1": "Flat 402, Prestige Shantiniketan, Whitefield", "city": "Bengaluru", "state": "KA",
            "postcode": "560048", "country": "IN"
        },
        "orders_count": 5,
        "total_spent": "52485.00",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    },
    {
        "id": 2,
        "date_created": "2026-02-10T14:15:20",
        "email": "priya.patel@kilowott.com",
        "first_name": "Priya",
        "last_name": "Patel",
        "role": "customer",
        "username": "priyap",
        "billing": {
            "first_name": "Priya", "last_name": "Patel", "company": "Kilowott Labs Goa",
            "address_1": "Villa 12, Ocean View Estates, Dona Paula", "city": "Panaji", "state": "GA",
            "postcode": "403004", "country": "IN", "email": "priya.patel@kilowott.com", "phone": "+91 98221 44332"
        },
        "shipping": {
            "first_name": "Priya", "last_name": "Patel",
            "address_1": "Villa 12, Ocean View Estates, Dona Paula", "city": "Panaji", "state": "GA",
            "postcode": "403004", "country": "IN"
        },
        "orders_count": 3,
        "total_spent": "26993.00",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    },
    {
        "id": 3,
        "date_created": "2026-03-01T09:00:00",
        "email": "rohan.mehta@yahoo.in",
        "first_name": "Rohan",
        "last_name": "Mehta",
        "role": "customer",
        "username": "rohanm",
        "billing": {
            "first_name": "Rohan", "last_name": "Mehta", "company": "Fintech Solutions",
            "address_1": "B-201, Lodha Bellissimo, Lower Parel", "city": "Mumbai", "state": "MH",
            "postcode": "400013", "country": "IN", "email": "rohan.mehta@yahoo.in", "phone": "+91 99200 55667"
        },
        "shipping": {
            "first_name": "Rohan", "last_name": "Mehta",
            "address_1": "B-201, Lodha Bellissimo, Lower Parel", "city": "Mumbai", "state": "MH",
            "postcode": "400013", "country": "IN"
        },
        "orders_count": 2,
        "total_spent": "10498.00",
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150"
    },
    {
        "id": 4,
        "date_created": "2026-03-12T16:40:00",
        "email": "ananya.iyer@outlook.com",
        "first_name": "Ananya",
        "last_name": "Iyer",
        "role": "customer",
        "username": "ananyai",
        "billing": {
            "first_name": "Ananya", "last_name": "Iyer", "company": "Cognizant Tech",
            "address_1": "Plot 88, Adyar Riverside, Besant Nagar", "city": "Chennai", "state": "TN",
            "postcode": "600090", "country": "IN", "email": "ananya.iyer@outlook.com", "phone": "+91 98401 77889"
        },
        "shipping": {
            "first_name": "Ananya", "last_name": "Iyer",
            "address_1": "Plot 88, Adyar Riverside, Besant Nagar", "city": "Chennai", "state": "TN",
            "postcode": "600090", "country": "IN"
        },
        "orders_count": 1,
        "total_spent": "8499.00",
        "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150"
    },
    {
        "id": 5,
        "date_created": "2026-04-05T11:22:10",
        "email": "vikram.malhotra@rediffmail.com",
        "first_name": "Vikram",
        "last_name": "Malhotra",
        "role": "customer",
        "username": "vikramm",
        "billing": {
            "first_name": "Vikram", "last_name": "Malhotra", "company": "Delhi Logistics Corp",
            "address_1": "C-14, Hauz Khas Enclave", "city": "New Delhi", "state": "DL",
            "postcode": "110016", "country": "IN", "email": "vikram.malhotra@rediffmail.com", "phone": "+91 98110 33221"
        },
        "shipping": {
            "first_name": "Vikram", "last_name": "Malhotra",
            "address_1": "C-14, Hauz Khas Enclave", "city": "New Delhi", "state": "DL",
            "postcode": "110016", "country": "IN"
        },
        "orders_count": 1,
        "total_spent": "2499.00",
        "avatar_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150"
    }
]

# India-Specific Orders (in INR with UPI, Razorpay, Netbanking, COD)
SEEDED_ORDERS = [
    {
        "id": 5001,
        "number": "5001",
        "status": "completed",
        "currency": "INR",
        "date_created": "2026-03-20T11:00:00",
        "date_modified": "2026-03-21T15:30:00",
        "total": "24494.00",
        "total_tax": "3736.00",
        "shipping_total": "0.00",
        "customer_id": 1,
        "billing": SEEDED_CUSTOMERS[0]["billing"],
        "shipping": SEEDED_CUSTOMERS[0]["shipping"],
        "payment_method": "upi",
        "payment_method_title": "UPI (Google Pay / PhonePe)",
        "customer_note": "Please call security desk at Prestige Shantiniketan gate upon arrival.",
        "line_items": [
            {"id": 1, "name": "OnePlus 32-inch Y Series HD Android TV", "product_id": 103, "quantity": 1, "subtotal": "14999.00", "total": "14999.00", "price": 14999.0},
            {"id": 2, "name": "Logitech MX Master 3S Wireless Mouse", "product_id": 104, "quantity": 1, "subtotal": "9495.00", "total": "9495.00", "price": 9495.0}
        ]
    },
    {
        "id": 5002,
        "number": "5002",
        "status": "processing",
        "currency": "INR",
        "date_created": "2026-04-01T14:20:00",
        "date_modified": "2026-04-01T14:22:00",
        "total": "10498.00",
        "total_tax": "1600.00",
        "shipping_total": "0.00",
        "customer_id": 2,
        "billing": SEEDED_CUSTOMERS[1]["billing"],
        "shipping": SEEDED_CUSTOMERS[1]["shipping"],
        "payment_method": "razorpay",
        "payment_method_title": "Razorpay (Credit Card / Netbanking)",
        "customer_note": "Deliver during working hours to Kilowott Labs Dona Paula office.",
        "line_items": [
            {"id": 3, "name": "Keychron K2 Wireless Mechanical Keyboard (RGB)", "product_id": 102, "quantity": 1, "subtotal": "8499.00", "total": "8499.00", "price": 8499.0},
            {"id": 4, "name": "boAt Rockerz 550 Wireless Over-Ear Headphones", "product_id": 101, "quantity": 1, "subtotal": "1999.00", "total": "1999.00", "price": 1999.0}
        ]
    },
    {
        "id": 5003,
        "number": "5003",
        "status": "pending",
        "currency": "INR",
        "date_created": "2026-04-08T09:15:00",
        "date_modified": "2026-04-08T09:15:00",
        "total": "8499.00",
        "total_tax": "1296.00",
        "shipping_total": "0.00",
        "customer_id": 4,
        "billing": SEEDED_CUSTOMERS[3]["billing"],
        "shipping": SEEDED_CUSTOMERS[3]["shipping"],
        "payment_method": "cod",
        "payment_method_title": "Cash on Delivery (COD)",
        "customer_note": "Ensure delivery before Friday",
        "line_items": [
            {"id": 5, "name": "Keychron K2 Wireless Mechanical Keyboard (RGB)", "product_id": 102, "quantity": 1, "subtotal": "8499.00", "total": "8499.00", "price": 8499.0}
        ]
    },
    {
        "id": 5004,
        "number": "5004",
        "status": "completed",
        "currency": "INR",
        "date_created": "2026-04-02T16:00:00",
        "date_modified": "2026-04-03T18:00:00",
        "total": "9495.00",
        "total_tax": "1448.00",
        "shipping_total": "0.00",
        "customer_id": 3,
        "billing": SEEDED_CUSTOMERS[2]["billing"],
        "shipping": SEEDED_CUSTOMERS[2]["shipping"],
        "payment_method": "netbanking",
        "payment_method_title": "HDFC NetBanking (Direct Pay)",
        "customer_note": "",
        "line_items": [
            {"id": 6, "name": "Logitech MX Master 3S Wireless Mouse", "product_id": 104, "quantity": 1, "subtotal": "9495.00", "total": "9495.00", "price": 9495.0}
        ]
    },
    {
        "id": 5005,
        "number": "5005",
        "status": "on-hold",
        "currency": "INR",
        "date_created": "2026-04-10T12:00:00",
        "date_modified": "2026-04-10T12:05:00",
        "total": "2499.00",
        "total_tax": "381.00",
        "shipping_total": "150.00",
        "customer_id": 5,
        "billing": SEEDED_CUSTOMERS[4]["billing"],
        "shipping": SEEDED_CUSTOMERS[4]["shipping"],
        "payment_method": "upi",
        "payment_method_title": "UPI (Paytm)",
        "customer_note": "Awaiting bank reference UTR confirmation.",
        "line_items": [
            {"id": 7, "name": "Noise ColorFit Pulse 3 Smartwatch (AMOLED)", "product_id": 105, "quantity": 1, "subtotal": "2499.00", "total": "2499.00", "price": 2499.0}
        ]
    }
]

_customers_db = copy.deepcopy(SEEDED_CUSTOMERS)
_orders_db = copy.deepcopy(SEEDED_ORDERS)
_products_db = copy.deepcopy(SEEDED_PRODUCTS)


@sandbox_router.get("/customers", response_model=List[Dict[str, Any]])
def get_customers(
    email: Optional[str] = None,
    per_page: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    results = _customers_db
    if email:
        results = [c for c in results if c.get("email", "").lower() == email.lower()]
    start = (page - 1) * per_page
    return results[start:start + per_page]


@sandbox_router.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    customer = next((c for c in _customers_db if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="WooCommerce customer not found")
    return customer


@sandbox_router.post("/customers", status_code=201)
def create_customer(payload: Dict[str, Any]):
    new_id = max((c["id"] for c in _customers_db), default=0) + 1
    now_str = datetime.utcnow().isoformat()
    customer = {
        "id": new_id,
        "date_created": now_str,
        "email": payload.get("email"),
        "first_name": payload.get("first_name", ""),
        "last_name": payload.get("last_name", ""),
        "role": "customer",
        "username": payload.get("username", payload.get("email", "").split("@")[0]),
        "billing": payload.get("billing", {}),
        "shipping": payload.get("shipping", {}),
        "orders_count": 0,
        "total_spent": "0.00",
        "avatar_url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150"
    }
    _customers_db.append(customer)
    return customer


@sandbox_router.get("/orders", response_model=List[Dict[str, Any]])
def get_orders(
    status: Optional[str] = None,
    customer: Optional[int] = None,
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    results = _orders_db
    if status and status != "any":
        results = [o for o in results if o.get("status") == status]
    if customer:
        results = [o for o in results if o.get("customer_id") == customer]
    start = (page - 1) * per_page
    return results[start:start + per_page]


@sandbox_router.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in _orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="WooCommerce order not found")
    return order


@sandbox_router.post("/orders", status_code=201)
def create_order(payload: Dict[str, Any]):
    new_id = max((o["id"] for o in _orders_db), default=5000) + 1
    now_str = datetime.utcnow().isoformat()
    order = {
        "id": new_id,
        "number": str(new_id),
        "status": payload.get("status", "pending"),
        "currency": payload.get("currency", "INR"),
        "date_created": now_str,
        "date_modified": now_str,
        "total": str(payload.get("total", "2499.00")),
        "total_tax": str(payload.get("total_tax", "380.00")),
        "shipping_total": str(payload.get("shipping_total", "0.00")),
        "customer_id": payload.get("customer_id", 0),
        "billing": payload.get("billing", {}),
        "shipping": payload.get("shipping", {}),
        "payment_method": payload.get("payment_method", "upi"),
        "payment_method_title": payload.get("payment_method_title", "UPI (PhonePe / GPay)"),
        "customer_note": payload.get("customer_note", ""),
        "line_items": payload.get("line_items", [])
    }
    _orders_db.append(order)
    return order


@sandbox_router.put("/orders/{order_id}")
def update_order(order_id: int, payload: Dict[str, Any]):
    order = next((o for o in _orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="WooCommerce order not found")
    
    if "status" in payload:
        order["status"] = payload["status"]
    if "customer_note" in payload:
        order["customer_note"] = payload["customer_note"]
    order["date_modified"] = datetime.utcnow().isoformat()
    return order


@sandbox_router.get("/products", response_model=List[Dict[str, Any]])
def get_products():
    return _products_db


@sandbox_router.post("/reset-sandbox")
def reset_sandbox():
    global _customers_db, _orders_db, _products_db
    _customers_db = copy.deepcopy(SEEDED_CUSTOMERS)
    _orders_db = copy.deepcopy(SEEDED_ORDERS)
    _products_db = copy.deepcopy(SEEDED_PRODUCTS)
    return {"message": "WooCommerce sandbox reset successfully with Indian dataset."}
