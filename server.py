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
    msg['Subject'] = f"✅ Order Confirmed: {'#'}{order_id} | ProteinKart"
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
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap"
                rel="stylesheet">
            <style>
                body { margin: 0;  padding: 0; background-color: #F1F5F9; font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif; -webkit-font-smoothing: antialiased;}
            </style>
        </head>
        
        <body>
            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#F1F5F9; padding:32px 16px;">
                <tr>
                    <td align="center">
                        <table width="620" border="0" cellspacing="0" cellpadding="0"
                            style="background:#fff; border-radius:20px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.07); border:1px solid #E2E8F0;">
        
                            <!-- TOP BANNER -->
                            <tr>
                                <td
                                    style="background: linear-gradient(135deg, #0d2c24 0%, #1a4d3a 100%); padding: 36px 48px; text-align:center;">
                                    <div
                                        style="font-size:10px; color:#d4af37; letter-spacing:6px; text-transform:uppercase; margin-bottom:10px; font-weight:600;">
                                        Premium Nutrition</div>
                                    <div
                                        style="font-size:28px; font-weight:800; color:#ffffff; letter-spacing:5px; text-transform:uppercase;">
                                        PROTEINKART</div>
                                    <div style="height:2px; width:48px; background:#d4af37; margin:14px auto 0;"></div>
                                </td>
                            </tr>
        
                            <!-- SHIPPED HERO -->
                            <tr>
                                <td style="padding:40px 48px 0; text-align:center;">
                                    <div style="font-size:56px; margin-bottom:16px;">📦</div>
                                    <div
                                        style="font-size:13px; color:#4F46E5; font-weight:700; letter-spacing:3px; text-transform:uppercase; margin-bottom:10px;">
                                        Order Shipped</div>
                                    <div
                                        style="font-size:30px; font-weight:800; color:#0F172A; letter-spacing:-0.5px; margin-bottom:12px;">
                                        It's on its way, {customer_name.split()[0]}! 💪</div>
                                    <div
                                        style="font-size:15px; color:#64748B; line-height:1.7; max-width:460px; margin:0 auto 32px;">
                                        Your ProteinKart order has been dispatched and is heading your way.
                                        Get your shaker ready — your fuel is almost here.
                                    </div>
                                </td>
                            </tr>
        
                            <!-- ARRIVAL CARD -->
                            <tr>
                                <td style="padding:0 48px;">
                                    <div
                                        style="background:linear-gradient(135deg, #EEF2FF, #E0E7FF); border-radius:16px; padding:28px 32px; border:1px solid #C7D2FE; text-align:center; margin-bottom:28px;">
                                        <div
                                            style="font-size:11px; color:#4F46E5; text-transform:uppercase; font-weight:700; letter-spacing:3px; margin-bottom:6px;">
                                            Estimated Delivery</div>
                                        <div style="font-size:26px; font-weight:800; color:#3730A3; margin-bottom:8px;">
                                            {arriving_date}</div>
                                        <div style="font-size:13px; color:#6366F1;">Order ID: <strong>{'#'}{order_id}</strong></div>
                                    </div>
                                </td>
                            </tr>
        
                            <!-- TRACKING STEPS -->
                            <tr>
                                <td style="padding:0 48px 32px;">
                                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td align="center" width="22%">
                                                <div
                                                    style="width:44px;height:44px;border-radius:12px;background:#4F46E5;display:inline-block;line-height:44px;color:#fff;font-size:18px;font-weight:700;">
                                                    ✓</div>
                                                <div
                                                    style="font-size:10px;margin-top:7px;color:#1E293B;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
                                                    Ordered</div>
                                                <div style="font-size:10px;color:#94A3B8;margin-top:2px;">{order_date}</div>
                                            </td>
                                            <td valign="top" style="padding-top:22px;">
                                                <div style="height:4px;background:#4F46E5;border-radius:2px;"></div>
                                            </td>
                                            <td align="center" width="22%">
                                                <div
                                                    style="width:44px;height:44px;border-radius:12px;background:#4F46E5;display:inline-block;line-height:44px;color:#fff;font-size:18px;">
                                                    ✓</div>
                                                <div
                                                    style="font-size:10px;margin-top:7px;color:#1E293B;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
                                                    Packed</div>
                                                <div style="font-size:10px;color:#94A3B8;margin-top:2px;">Today</div>
                                            </td>
                                            <td valign="top" style="padding-top:22px;">
                                                <div
                                                    style="height:4px;background:linear-gradient(to right,#4F46E5,#E2E8F0);border-radius:2px;">
                                                </div>
                                            </td>
                                            <td align="center" width="22%">
                                                <div
                                                    style="width:44px;height:44px;border-radius:12px;border:2.5px solid #6366F1;background:#EEF2FF;display:inline-block;line-height:40px;color:#6366F1;font-size:20px;box-sizing:border-box;">
                                                    🚚</div>
                                                <div
                                                    style="font-size:10px;margin-top:7px;color:#6366F1;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
                                                    In Transit</div>
                                                <div style="font-size:10px;color:#94A3B8;margin-top:2px;">En route</div>
                                            </td>
                                            <td valign="top" style="padding-top:22px;">
                                                <div style="height:4px;background:#E2E8F0;border-radius:2px;"></div>
                                            </td>
                                            <td align="center" width="22%">
                                                <div
                                                    style="width:44px;height:44px;border-radius:12px;border:2px solid #E2E8F0;background:#F8FAFC;display:inline-block;line-height:40px;color:#CBD5E1;font-size:20px;box-sizing:border-box;">
                                                    🏠</div>
                                                <div
                                                    style="font-size:10px;margin-top:7px;color:#94A3B8;font-weight:500;text-transform:uppercase;letter-spacing:1px;">
                                                    Delivered</div>
                                                <div style="font-size:10px;color:#CBD5E1;margin-top:2px;">Soon</div>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
        
                            <!-- DIVIDER -->
                            <tr>
                                <td style="padding:0 48px;">
                                    <div style="height:1px;background:#F1F5F9;"></div>
                                </td>
                            </tr>
        
                            <!-- ORDER SUMMARY -->
                            <tr>
                                <td style="padding:28px 48px;">
                                    <div
                                        style="font-size:12px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:2px; margin-bottom:16px;">
                                        Order Summary</div>
                                    <table width="100%" border="0" cellspacing="0" cellpadding="0"
                                        style="background:#F8FAFC; border-radius:14px; overflow:hidden; border:1px solid #E2E8F0;">
                                        <tr>
                                            <td style="padding:20px 24px; border-bottom:1px solid #E2E8F0;">
                                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                    <tr>
                                                        <td>
                                                            <div
                                                                style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:4px;">
                                                                {product}</div>
                                                            <div style="font-size:13px; color:#64748B;">Brand: {brand}
                                                                &nbsp;·&nbsp; Qty: {quantity}</div>
                                                        </td>
                                                        <td align="right">
                                                            <div style="font-size:16px; font-weight:800; color:#0F172A;
        ">₹{total_price:,}</div>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding:14px 24px; border-bottom:1px solid #E2E8F0;">
                                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                    <tr>
                                                        <td style="font-size:13px; color:#64748B;">Shipping</td>
                                                        <td align="right"
                                                            style="font-size:13px; color:#16A34A; font-weight:600;">FREE</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding:14px 24px;">
                                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                    <tr>
                                                        <td style="font-size:14px; font-weight:700; color:#0F172A;">Total Paid
                                                        </td>
                                                        <td align="right"
                                                            style="font-size:18px; font-weight:800; color:#4F46E5;">
                                                            ₹{total_price:,}</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
        
                            <!-- ORDER DETAILS GRID -->
                            <tr>
                                <td style="padding:0 48px 28px;">
                                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td width="50%" style="padding-right:8px;">
                                                <div
                                                    style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:16px 20px;">
                                                    <div
                                                        style="font-size:10px; color:#94A3B8; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:6px;">
                                                        Order ID</div>
                                                    <div style="font-size:14px; font-weight:700; color:#0F172A;">{'#'}{order_id}
                                                    </div>
                                                    <div style="font-size:12px; color:#64748B; margin-top:2px;">{order_date}
                                                    </div>
                                                </div>
                                            </td>
                                            <td width="50%" style="padding-left:8px;">
                                                <div
                                                    style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:16px 20px;">
                                                    <div
                                                        style="font-size:10px; color:#94A3B8; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:6px;">
                                                        Status</div>
                                                    <div
                                                        style="font-size:13px; font-weight:700; color:#16A34A; text-transform:capitalize;">
                                                        ✓ {status}</div>
                                                    <div style="font-size:12px; color:#64748B; margin-top:4px;">{customer_email}
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
        
                            <!-- TIPS BANNER -->
                            <tr>
                                <td style="padding:0 48px 32px;">
                                    <div
                                        style="background:linear-gradient(135deg, #0d2c24, #1a4d3a); border-radius:16px; padding:24px 28px;">
                                        <div
                                            style="font-size:13px; font-weight:700; color:#d4af37; margin-bottom:10px; letter-spacing:1px; text-transform:uppercase;">
                                            💡 Pro Tip While You Wait</div>
                                        <div style="font-size:14px; color:#CBD5E1; line-height:1.7;">
                                            Take your whey within <strong style="color:#fff;">30 minutes post-workout</strong>
                                            for maximum muscle synthesis. Mix with cold water or milk for best results.
                                            Consistency &gt; Perfection. 🏋️
                                        </div>
                                    </div>
                                </td>
                            </tr>
        
                            <!-- NEED HELP -->
                            <tr>
                                <td style="padding:0 48px 32px; text-align:center;">
                                    <div style="font-size:14px; color:#64748B; margin-bottom:12px;">Questions about your order?
                                    </div>
                                    <a href="mailto:support@proteinkart.in"
                                        style="display:inline-block; background:#0F172A; color:#ffffff; font-size:13px; font-weight:700; padding:12px 28px; border-radius:10px; text-decoration:none; letter-spacing:0.5px;">Contact
                                        Support</a>
                                </td>
                            </tr>
        
                            <!-- FOOTER -->
                            <tr>
                                <td
                                    style="background:#F8FAFC; border-top:1px solid #E2E8F0; padding:24px 48px; text-align:center;">
                                    <div style="font-size:18px; margin-bottom:8px;">💪 &nbsp; 🥛 &nbsp; 🏋️</div>
                                    <div style="font-size:12px; color:#94A3B8; margin-bottom:4px;">© 2026 ProteinKart. All
                                        rights reserved.</div>
                                    <div style="font-size:12px; color:#CBD5E1;">This email was sent to {customer_email}</div>
                                    <div style="margin-top:12px;">
                                        <a href="#"
                                            style="font-size:11px; color:#94A3B8; text-decoration:none; margin:0 8px;">Unsubscribe</a>
                                        <span style="color:#E2E8F0;">|</span>
                                        <a href="#"
                                            style="font-size:11px; color:#94A3B8; text-decoration:none; margin:0 8px;">Privacy
                                            Policy</a>
                                        <span style="color:#E2E8F0;">|</span>
                                        <a href="#"
                                            style="font-size:11px; color:#94A3B8; text-decoration:none; margin:0 8px;">Terms</a>
                                    </div>
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

