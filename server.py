"""
ProteinKart Backend — Startup REST API.
This service handles the protein catalog, orders, and real-time email notifications.

Usage:
  uvicorn server:app --host 0.0.0.0 --port 8000
"""

import os
import sqlite3
import smtplib
import ssl
from contextlib import contextmanager, asynccontextmanager
from typing import Optional
from email.message import EmailMessage

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

# ── CONFIGURATION ───────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "proteins.db"))
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# SMTP Config (Set these in your .env or GCP Environment Variables)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")      # e.g. your-name@gmail.com
SMTP_PASS = os.getenv("SMTP_PASS", "")      # e.g. your-app-password
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)


# ── DATABASE HELPERS ────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Seed the database if it doesn't already exist."""
    if os.path.exists(DB_PATH):
        return
    if not os.path.exists(SCHEMA_PATH):
        print("Warning: schema.sql not found. Database not initialized.")
        return
    with open(SCHEMA_PATH, "r") as f:
        sql = f.read()
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(sql)
    print(f"Startup Database created at {DB_PATH}")


# ── EMAIL SHOOTER ───────────────────────────────────────────
def send_confirmation_email(order_id: int, customer_name: str, customer_email: str, product: dict, quantity: int, total_price: int):
    """Sends a premium HTML order confirmation email."""
    if not SMTP_USER or not SMTP_PASS:
        print("SMTP credentials missing. Email shoot skipped.")
        return False

    msg = EmailMessage()
    msg['Subject'] = f"✅ Order Confirmed: #{order_id} | ProteinKart"
    msg['From'] = f"ProteinKart <{FROM_EMAIL}>"
    msg['To'] = customer_email

    # Plain text fallback
    text_content = f"Hi {customer_name}, your order #{order_id} for {product['name']} has been placed for ₹{total_price}."
    msg.set_content(text_content)

    # Premium HTML Version
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <!-- Hero Header -->
            <div style="background-color: #0d2c24; padding: 50px 20px; text-align: center;">
                <div style="color: #d4af37; font-size: 32px; font-family: 'Times New Roman', serif; letter-spacing: 4px; font-weight: 300;">PROTEINKART</div>
                <div style="height: 1px; width: 40px; background-color: #d4af37; margin: 15px auto;"></div>
                <p style="color: #f1f1f1; margin-top: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 2px;">The Gold Standard of Fuel</p>
            </div>
            
            <div style="padding: 40px 30px;">
                <h2 style="color: #0d2c24; margin-top: 0; font-weight: 400; letter-spacing: -0.5px;">Your recovery begins now.</h2>
                <p style="color: #666; line-height: 1.6;">Dear <strong>{customer_name}</strong>,</p>
                <p style="color: #666; line-height: 1.6;">We've received your order and our specialists are preparing your premium selection for dispatch.</p>
                
                <!-- Product Card -->
                <div style="display: flex; align-items: center; background-color: #fcfcfc; border: 1px solid #f0f0f0; padding: 25px; border-radius: 4px; margin-top: 30px;">
                    <img src="{product['image_url']}" alt="{product['name']}" style="width: 110px; height: 110px; object-fit: contain; border-radius: 2px;">
                    <div style="margin-left: 25px;">
                        <h4 style="margin: 0; color: #0d2c24; font-size: 18px; font-weight: 500;">{product['name']}</h4>
                        <p style="margin: 5px 0; color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">{product['brand']} | {product['type']}</p>
                        <p style="margin: 10px 0 0 0; color: #0d2c24; font-weight: 600; font-size: 16px;">{quantity} unit(s) &times; ₹{product['price']}</p>
                    </div>
                </div>

                <!-- Totals -->
                <div style="border-top: 1px solid #eee; margin-top: 40px; padding-top: 30px;">
                    <div style="display: flex; justify-content: space-between; font-size: 20px; color: #0d2c24;">
                        <span style="font-weight: 300;">Investment in Health</span>
                        <span style="font-weight: 600; color: #b8860b;">₹{total_price}</span>
                    </div>
                </div>

                <div style="text-align: center; margin-top: 50px;">
                    <a href="#" style="background-color: #0d2c24; color: #d4af37; padding: 18px 45px; text-decoration: none; border-radius: 2px; font-weight: 500; display: inline-block; letter-spacing: 1px; font-size: 14px;">TRACK SHIPMENT</a>
                </div>
            </div>

            <div style="background-color: #fbfbfb; padding: 30px; text-align: center; font-size: 11px; color: #aaa; border-top: 1px solid #f5f5f5;">
                <p style="margin-bottom: 5px;">&copy; 2026 ProteinKart India. Crafted for Excellence.</p>
                <p>Stay Disciplined. Stay Strong.</p>
            </div>

        </div>
    </body>
    </html>
    """
    msg.add_alternative(html_content, subtype='html')

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"Confirmation email 'shot' to {customer_email}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


# ── MODELS ──────────────────────────────────────────────────
class OrderRequest(BaseModel):
    product_id: int
    quantity: int
    customer_name: str
    customer_email: EmailStr  # Validates email format


# ── APP INITIALIZATION ──────────────────────────────────────
app = FastAPI(title="ProteinKart API", version="1.1.0")

@app.on_event("startup")
def startup_event():
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your student MCP domains
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── ROUTES ──────────────────────────────────────────────────
@app.get("/")
async def health_check():
    """Confirm the API is alive for GCP health checks."""
    return {"status": "ok", "service": "ProteinKart Backend"}

@app.get("/api/products")
def search_products(
    type: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None),
    q: Optional[str] = Query(None, description="Search name/brand"),
):
    """Catalog search with simple filtering."""
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if type: query += " AND type = ?"; params.append(type)
    if brand: query += " AND brand = ?"; params.append(brand)
    if max_price: query += " AND price <= ?"; params.append(max_price)
    if q:
        query += " AND (name LIKE ? OR brand LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like])

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    """Fetch single product details."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)

@app.post("/api/orders")
def place_order(order: OrderRequest):
    """Place order + trigger Real Email Shoot."""
    with get_db() as conn:
        product = conn.execute("SELECT * FROM products WHERE id = ?", (order.product_id,)).fetchone()
        if not product: raise HTTPException(status_code=404, detail="Product not found")

        total_price = product["price"] * order.quantity
        cursor = conn.execute(
            "INSERT INTO orders (customer_name, customer_email, product_id, quantity, total_price) VALUES (?, ?, ?, ?, ?)",
            (order.customer_name, order.customer_email, order.product_id, order.quantity, total_price),
        )
        conn.commit()
        order_id = cursor.lastrowid

    # Trigger Real Email Shoot (Passing full product dict for rich HTML)
    send_confirmation_email(order_id, order.customer_name, order.customer_email, dict(product), order.quantity, total_price)

    return {
        "order_id": order_id,
        "product": product["name"],
        "brand": product["brand"],
        "quantity": order.quantity,
        "total_price": total_price,
        "status": "placed",
        "customer_email": order.customer_email,
        "message": f"Order #{order_id} confirmed. Email shot to {order.customer_email}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

