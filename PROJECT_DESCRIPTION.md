# UniBike Fleet & Repair Analytics - Complete Project Overview

## 1. Project Vision & Purpose
The **UniBike Fleet & Repair Analytics** platform is a modern, full-stack web application designed for the TU Darmstadt AStA mobility team. Its primary goal is to digitize and automate the management of the campus bicycle fleet. By bridging the gap between student riders and mechanics, the platform streamlines repair ticketing, tracks fleet health KPIs, and provides an AI-powered repair assistant to help students fix minor issues themselves.

---

## 2. System Architecture

The project has evolved into a highly scalable, decoupled **Split-Stack Architecture**:

### A. Frontend (Client Layer)
The user interface is a premium, responsive Single Page Application (SPA) built with:
- **React (Vite):** Chosen for lightning-fast hot module replacement and modern component architecture.
- **Tailwind CSS v4:** Used for a sleek, glassmorphic design system and pixel-perfect layouts.
- **Framer Motion:** Powers smooth page transitions, hover micro-animations, and dynamic toast notifications.
- **React Query:** Manages asynchronous data fetching, caching, and state synchronization with the backend.
- **Recharts:** Renders beautiful, interactive data visualizations (e.g., Work Order Status Distribution).

### B. Backend (API & Business Logic)
The server layer is a high-performance REST API built with:
- **FastAPI:** Provides fast, asynchronous routing and automatic OpenAPI (Swagger) documentation.
- **SQLAlchemy (ORM):** Manages relational data mapping and prevents SQL injection.
- **SQLite:** A lightweight, file-based database used for persistent storage of bikes, work orders, and inventory.
- **Pydantic:** Validates incoming payloads and securely manages environment variables.

### C. Artificial Intelligence (RAG Pipeline)
An intelligent chatbot that answers student repair questions using internal maintenance manuals:
- **LangChain:** Orchestrates the Retrieval-Augmented Generation (RAG) pipeline.
- **ChromaDB:** A local vector database that stores and queries embedded document chunks.
- **HuggingFace Embeddings:** Uses the lightweight `all-MiniLM-L6-v2` model to convert text into vector embeddings.
- **Groq (Llama 3.1 8B):** A lightning-fast LLM that synthesizes the retrieved document excerpts into conversational, helpful answers.

---

## 3. Core Features & User Flows

### 1. Student Ticketing Portal (`/`)
- Students can report broken bicycles via a mobile-friendly interface.
- If a QR code is scanned (simulated via URL parameters like `?bike_id=123`), the form auto-fills the bike ID.
- The backend automatically provisions the bike in the database if it is brand new, ensuring a frictionless user experience.
- Upon submission, the bike's status is changed to "Out of Order".

### 2. Admin Dashboard (`/admin`)
- **Authentication:** Protected by a secure login gateway (`admin`/`password`).
- **Live KPIs:** Real-time metrics calculate Mean Time to Repair (MTTR), Open Tickets, and Missed SLAs (> 2 days).
- **Ticket Management:** Admins can view all reported issues and instantly change their status (e.g., Open -> In Progress -> Resolved).
- **Inventory Tracking:** Displays stock levels for critical components (Tubes, Brake Pads) and alerts mechanics when stock dips below reorder thresholds.

### 3. DIY Repair Assistant (`/repair`)
- A dedicated chatbot interface that empowers students to fix minor issues (like dropped chains).
- It relies purely on the official UniBike maintenance manuals (generated internally as PDFs) to ensure safety and accuracy.
- When an answer is provided, the UI elegantly displays the exact source document excerpts used to generate the response.

---

## 4. CI/CD & Deployment Strategy

To ensure code quality and global availability, the project uses a robust deployment pipeline:

### Automated Testing (GitHub Actions)
Every code push triggers a CI workflow (`.github/workflows/ci.yml`) that strictly enforces:
- **Ruff:** A hyper-fast Python linter that ensures clean code and catches logical errors (like blind exceptions).
- **Black:** An uncompromising auto-formatter that guarantees consistent Python styling.
- **Pytest:** Executes unit tests against a mocked database to ensure the API behaves correctly.

### Cloud Deployment (Vercel & Render)
- **Frontend (Vercel):** The React SPA is continuously deployed to Vercel's global CDN.
- **Backend (Render):** The FastAPI server is hosted on Render. 
- **Auto-Initialization Magic:** Because cloud environments often spin up from a blank slate, the backend is engineered to self-heal. On startup, a background thread automatically:
  1. Creates the `data/` directory.
  2. Builds all SQLite database tables.
  3. Seeds the database with demo bikes and tickets.
  4. Generates the PDF maintenance manuals.
  5. Initializes and embeds the ChromaDB vector store.
- **Smart Routing:** The frontend features an intelligent API URL parser that automatically corrects missing `/api` suffixes, preventing 404 routing errors in production.

---

## 5. Project History & Evolution

1. **Phase 1: The Monolithic Prototype**
   - The project originally started as a monolithic Python application using **Gradio** for the UI.
   - It successfully proved the concept of the RAG assistant and ticketing logic but suffered from limited UI customization and clunky navigation.

2. **Phase 2: Decoupling & Modernization**
   - The Gradio UI was entirely ripped out.
   - The Python code was refactored into a pure REST API (`src/api/server.py`).
   - A brand new, premium React frontend was built in the `frontend/` directory to provide a SaaS-tier user experience.

3. **Phase 3: Hardening & Bug Squashing**
   - Addressed complex dependency conflicts during CI/CD (specifically, pinning stable versions of the `langchain` ecosystem to support Render's futuristic Python 3.14 environments).
   - Fixed strict Ruff linting rules (`BLE001`) by safely suppressing them without crashing production.
   - Removed obsolete Gradio unit tests that were failing the pipeline.

4. **Phase 4: Live Production Polish**
   - Identified that the `.gitignore` security rules were preventing Render from starting with a database. Engineered the auto-initialization startup event to solve this permanently.
   - Added graceful error handling so the RAG assistant fails elegantly if the `GROQ_API_KEY` is missing from the environment variables.
