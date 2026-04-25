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

    from datetime import datetime, timedelta
    arriving_date = (datetime.now() + timedelta(days=3)).strftime("%A, %B %dth")

    # Premium HTML Version (Refined based on Nakpro/Shiprocket visuals)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #F8FAFC;
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                -webkit-font-smoothing: antialiased;
            }}
        </style>
    </head>
    <body>
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F8FAFC; padding: 20px;">
            <tr>
                <td align="center">
                    <!-- Outer Container -->
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;">
                        
                        <!-- Header -->
                        <tr>
                            <td align="center" style="padding: 40px 0; background: #ffffff;">
                                <div style="font-size: 24px; font-weight: 800; color: #0d2c24; letter-spacing: 4px; text-transform: uppercase;">PROTEINKART</div>
                                <div style="height: 2px; width: 40px; background-color: #d4af37; margin: 12px auto;"></div>
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td align="center" style="padding: 0 40px;">
                                <!-- Delivery Illustration -->
                                <div style="margin-bottom: 24px;">
                                    <img src="https://cdn-icons-png.flaticon.com/512/2311/2311524.png" width="100" alt="Shipping" style="display: block; margin: 0 auto;">
                                </div>

                                <div style="font-size: 16px; color: #64748B; margin-bottom: 8px;">Hi <strong>{customer_name}</strong>,</div>
                                <div style="font-size: 28px; font-weight: 800; color: #0F172A; margin-bottom: 12px; letter-spacing: -0.5px;">Your order has been shipped!</div>
                                <div style="font-size: 15px; color: #64748B; margin-bottom: 32px; line-height: 1.6; max-width: 480px;">
                                    We have shipped your ProteinKart order. Your fuel is on its way to help you crush your fitness goals.
                                </div>
                                
                                <!-- Arriving Section -->
                                <div style="background-color: #EEF2FF; border-radius: 16px; padding: 24px; margin-bottom: 40px; border: 1px solid #E0E7FF;">
                                    <div style="font-size: 12px; color: #4F46E5; text-transform: uppercase; font-weight: 700; letter-spacing: 2px; margin-bottom: 4px;">Estimated Arrival</div>
                                    <div style="font-size: 32px; font-weight: 800; color: #4F46E5;">{arriving_date}</div>
                                </div>

                                <!-- Tracking Progress Bar -->
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 48px;">
                                    <tr>
                                        <!-- Order Placed (Marked) -->
                                        <td align="center" width="25%">
                                            <div style="width: 40px; height: 40px; border-radius: 12px; background-color: #4F46E5; display: inline-block; line-height: 40px; color: white; font-size: 18px;">✓</div>
                                            <div style="font-size: 11px; margin-top: 8px; color: #1E293B; font-weight: 600;">Ordered</div>
                                        </td>
                                        <!-- Line 1 -->
                                        <td valign="top" style="padding-top: 20px;">
                                            <div style="height: 4px; background-color: #4F46E5; border-radius: 2px;"></div>
                                        </td>
                                        <!-- Shipped (Unmarked) -->
                                        <td align="center" width="25%">
                                            <div style="width: 40px; height: 40px; border-radius: 12px; border: 2px solid #E2E8F0; background-color: #F8FAFC; display: inline-block; line-height: 36px; color: #94A3B8; font-size: 18px; box-sizing: border-box;">📦</div>
                                            <div style="font-size: 11px; margin-top: 8px; color: #94A3B8; font-weight: 500;">Shipped</div>
                                        </td>
                                        <!-- Line 2 -->
                                        <td valign="top" style="padding-top: 20px;">
                                            <div style="height: 4px; background-color: #E2E8F0; border-radius: 2px;"></div>
                                        </td>
                                        <!-- In Transit (Unmarked) -->
                                        <td align="center" width="25%">
                                            <div style="width: 40px; height: 40px; border-radius: 12px; border: 2px solid #E2E8F0; background-color: #F8FAFC; display: inline-block; line-height: 36px; color: #94A3B8; font-size: 18px; box-sizing: border-box;">🚚</div>
                                            <div style="font-size: 11px; margin-top: 8px; color: #94A3B8; font-weight: 500;">In Transit</div>
                                        </td>
                                        <!-- Line 3 -->
                                        <td valign="top" style="padding-top: 20px;">
                                            <div style="height: 4px; background-color: #E2E8F0; border-radius: 2px;"></div>
                                        </td>
                                        <!-- Delivered (Unmarked) -->
                                        <td align="center" width="25%">
                                            <div style="width: 40px; height: 40px; border-radius: 12px; border: 2px solid #E2E8F0; background-color: #F8FAFC; display: inline-block; line-height: 36px; color: #94A3B8; font-size: 18px; box-sizing: border-box;">🏠</div>
                                            <div style="font-size: 11px; margin-top: 8px; color: #94A3B8; font-weight: 500;">Delivered</div>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Track Button -->
                                <div style="margin-bottom: 48px;">
                                    <a href="#" style="background-color: #22C55E; color: white; padding: 18px 48px; text-decoration: none; border-radius: 12px; font-weight: 700; display: inline-block; font-size: 16px; box-shadow: 0 10px 20px rgba(34, 197, 94, 0.2);">Track Your Order</a>
                                </div>
                            </td>
                        </tr>

                        <!-- Order Details -->
                        <tr>
                            <td style="padding: 40px; background-color: #F8FAFC; border-top: 1px solid #E2E8F0;">
                                <div style="font-size: 18px; font-weight: 700; color: #0F172A; margin-bottom: 24px;">Shipment Summary</div>
                                
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 12px; border: 1px solid #E2E8F0; overflow: hidden;">
                                    <tr>
                                        <td width="120" style="padding: 20px;">
                                            <img src="{product['image_url']}" width="100" height="100" style="object-fit: contain; border-radius: 8px; border: 1px solid #F1F5F9;">
                                        </td>
                                        <td style="padding: 20px 20px 20px 0;">
                                            <div style="font-size: 16px; font-weight: 700; color: #0F172A; margin-bottom: 4px;">{product['name']}</div>
                                            <div style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Qty: {quantity} | {product['brand']}</div>
                                            
                                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                <tr>
                                                    <td style="font-size: 14px; color: #64748B;">Amount</td>
                                                    <td align="right" style="font-size: 14px; color: #0F172A; font-weight: 600;">₹{product['price']}</td>
                                                </tr>
                                                <tr>
                                                    <td style="font-size: 14px; color: #64748B; padding-top: 4px;">Shipping</td>
                                                    <td align="right" style="font-size: 14px; color: #22C55E; font-weight: 600; padding-top: 4px;">FREE</td>
                                                </tr>
                                                <tr>
                                                    <td style="font-size: 16px; color: #0F172A; font-weight: 700; padding-top: 16px; border-top: 1px solid #F1F5F9; margin-top: 12px;">Total Paid</td>
                                                    <td align="right" style="font-size: 18px; color: #0F172A; font-weight: 800; padding-top: 16px; border-top: 1px solid #F1F5F9; margin-top: 12px;">₹{total_price}</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Shipping Info -->
                        <tr>
                            <td style="padding: 40px; background-color: #ffffff;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td width="50%" valign="top" style="padding-right: 20px;">
                                            <div style="font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">Delivery Address</div>
                                            <div style="font-size: 14px; color: #1E293B; line-height: 1.6;">
                                                <strong>{customer_name}</strong><br>
                                                5/3, Gomti Niwas, Vijay Nagar<br>
                                                Indore, MP 452010
                                            </div>
                                        </td>
                                        <td width="50%" valign="top" style="padding-left: 20px; border-left: 1px solid #E2E8F0;">
                                            <div style="font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">Order Info</div>
                                            <div style="font-size: 13px; color: #64748B; margin-bottom: 6px;">Order ID: <span style="color: #0F172A; font-weight: 600;">#{order_id}</span></div>
                                            <div style="font-size: 13px; color: #64748B; margin-bottom: 6px;">Courier: <span style="color: #0F172A; font-weight: 600;">BLUE DART</span></div>
                                            <div style="font-size: 13px; color: #64748B;">AWB No: <span style="color: #4F46E5; font-weight: 600;">PK{order_id}SHP</span></div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding: 40px; background-color: #0d2c24;">
                                <div style="font-size: 18px; font-weight: 800; color: #d4af37; letter-spacing: 3px; margin-bottom: 8px;">PROTEINKART</div>
                                <div style="font-size: 11px; color: #7A8E89; margin-bottom: 24px;">The Gold Standard of Performance Fuel</div>
                                <div style="height: 1px; width: 60px; background-color: #1a4d3f; margin-bottom: 24px;"></div>
                                <div style="font-size: 10px; color: #d4af37; text-transform: uppercase; letter-spacing: 2px;">Stay Strong. Stay Disciplined.</div>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Bottom bar -->
                    <div style="height: 6px; width: 600px; background: linear-gradient(90deg, #4F46E5 0%, #22C55E 100%); border-radius: 0 0 16px 16px;"></div>
                    
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="margin-top: 24px;">
                        <tr>
                            <td align="center" style="font-size: 12px; color: #94A3B8;">
                                &copy; 2026 ProteinKart India. All Rights Reserved.<br>
                                <a href="#" style="color: #94A3B8; text-decoration: underline;">Unsubscribe</a> | <a href="#" style="color: #94A3B8; text-decoration: underline;">Support</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
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

