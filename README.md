# KILOWOTT CRM — WooCommerce Intelligent Integration Suite

[![Pytest Tests](https://img.shields.io/badge/pytest-passing-success.svg)](backend/tests)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![WooCommerce](https://img.shields.io/badge/WooCommerce-REST%20v3%20Compatible-96588a.svg)](https://woocommerce.github.io/woocommerce-rest-api-docs/)

Enterprise-grade Customer Relationship Management (CRM) system designed and implemented for the **Kilowott Hackathon Challenge**.

Deeply integrates with WooCommerce to deliver:
1. **Customer Data Management & 360° Profiles** (RFM Segmentation, LTV, AOV, Tagging).
2. **Order Tracking Pipeline** (Full lifecycle tracking, line item breakdowns, bidirectional status sync).
3. **Automated Communication Workflows** (Event-driven email/SMS/ticket automations).

---

## 🚀 Quick Start (Running Locally)

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Start the Backend API Server
```powershell
# Open terminal in project root
.\backend\.venv\Scripts\activate
python backend/run.py
```
- The backend will start on **http://127.0.0.1:8000**
- Interactive Swagger API Docs: **http://127.0.0.1:8000/docs**
- WooCommerce REST API Sandbox: **http://127.0.0.1:8000/wp-json/wc/v3**

### 2. Start the Frontend Dashboard
```powershell
# In a second terminal
cd frontend
npm run dev
```
- Open your browser to **http://localhost:5173**

---

## 🧪 Running Automated Tests

Demonstrating codebase quality with our unit and integration test suite:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest -v backend\tests
```
**Test Coverage Includes:**
- Customer tier & RFM scoring calculation logic
- WooCommerce webhook processing & order creation
- Customer financial metric updates (LTV, AOV, order frequency)
- Automated workflow trigger dispatch
- REST API endpoint health & sandbox responses

---

## 🏛️ System Architecture & Design Patterns

- **Adapter Pattern (`backend/app/services/woocommerce_client.py`):** Normalizes requests to standard WooCommerce REST API v3 specifications. Switch from the included test sandbox to any live WordPress site simply by updating `WOOCOMMERCE_BASE_URL` in `.env`.
- **Event-Driven Webhook Pipeline (`backend/app/api/webhook_routes.py`):** Ingests incoming store events (`order.created`, `order.updated`, `customer.created`) in real-time.
- **Repository / Service Pattern (`backend/app/services/crm_service.py`):** Decouples business logic, aggregation math, and workflow logic from HTTP transport layers.
- **Glassmorphism Design System (`frontend/src/index.css`):** Custom high-contrast, responsive dashboard UI built with modern CSS tokens.

For complete architectural diagrams and schemas, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).


---

## 🤖 Phase 2: Agentic AI Integration Roadmap

The stack was deliberately built with **Python (FastAPI + Pydantic)** to facilitate seamless Phase 2 Agentic AI integration:
- **LLM Function Calling:** CRM service methods (`get_customer_profile`, `get_orders`, `send_communication`) are pre-structured as Pydantic tools.
- **Autonomous Support Agents:** Plug in LangGraph, CrewAI, or Google Gemini/OpenAI SDK to handle automated ticket replies and order lookups.
- **Churn Prediction Engine:** An agent analyzing recency and sentiment in support notes to tag customers as high-churn risk.

---

## Link to the Videos
https://drive.google.com/drive/folders/167banlJSG_L--8NuUMmC838FZMQJPfvz?usp=drive_link
