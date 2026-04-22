# Workshop: Build Your ProteinKart MCP Server

Welcome to the ProteinKart Agentic Workshop! You are building an **MCP (Model Context Protocol) Server** that will act as the "Agentic UI" for our startup's protein delivery service.

## 1. Central Backend (The Startup)
We have a central ProteinKart Backend running that manages the product catalog and order processing. Your job is to build the tool layer that lets agents (like Gemini or Claude) talk to it.

**Backend API Base URL:** `[YOUR_DEPLOYED_BACKEND_URL_HERE]`

---

## 2. Technical Specifications

### **Data Schema (Sqlite)**
If you were querying the database directly, this is the schema. Use this to understand the data types:

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT, brand TEXT, type TEXT, flavour TEXT,
    weight_kg REAL, price INTEGER,
    protein_per_serving INTEGER, servings INTEGER,
    rating REAL, certified BOOLEAN, veg BOOLEAN,
    in_stock BOOLEAN
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_name TEXT, customer_email TEXT,
    product_id INTEGER, quantity INTEGER, total_price INTEGER
);
```

### **API Endpoints**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/products` | Search catalog. Query params: `q`, `type`, `brand`, `max_price`. |
| `GET` | `/api/products/{id}` | Get full product info. |
| `POST` | `/api/orders` | Place an order. Payload: `{product_id, quantity, customer_name, customer_email}`. |

---

## 3. The "One-Prompt" MCP Builder

Copy and paste the prompt below into your favorite AI coding assistant (Gemini, Claude, or Antigravity) to build your server in seconds.

> **Note on Images:** Modern AI clients (like Claude and Antigravity) can render images if you return them in Markdown format: `![Product Image](url)`.

> **The Prompt:**
> "I need to build a Python MCP server using the `mcp[cli]` and `httpx` libraries for a startup called ProteinKart. 
> 
> The backend API is located at: **[YOUR_DEPLOYED_BACKEND_URL_HERE]**
> 
> Build an MCP server that exposes 3 tools:
> 1. `search_proteins`: Connects to `GET /api/products`. Support filters. **Include a small Markdown thumbnail for each product in the list.**
> 2. `get_protein_details`: Connects to `GET /api/products/{id}`. **Include a large Markdown image of the product at the top of the description.**
> 3. `place_order`: Connects to `POST /api/orders`. 
> 
> Ensure the tools return helpful, human-readable strings for the agent. Use `FastMCP` from the `mcp.server.fastmcp` package. Host the server over SSE (Server-Sent Events) on port 3000."

---

## 4. How to Test Your Server

1. **Install Dependencies:**
   ```bash
   pip install mcp[cli] httpx python-dotenv
   ```
2. **Run your server:**
   ```bash
   python mcp_server.py
   ```
3. **Connect to IDE:**
   Go to your IDE settings (Antigravity/Claude Desktop), add a new MCP server with the URL: `http://localhost:3000/sse`.

4. **Chat with your Agent:**
   "Show me chocolate whey proteins under ₹3000" -> "Order 1 unit of the best rated one for [Your Name]".
