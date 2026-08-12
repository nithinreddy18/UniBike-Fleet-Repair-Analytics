# 🚲 UniBike Fleet & Repair Analytics

## 🎯 Use Case
UniBike Fleet & Repair Analytics is a full-stack web application designed for a university student union (like AStA) to manage a campus bicycle fleet. 

Managing a shared bicycle fleet involves tracking broken bikes, managing repairs, and keeping track of inventory (spare parts). This project solves these challenges by providing:
1. A **Public Ticketing Portal** where anyone can report a broken bike.
2. A **Public AI Repair Assistant** where users can ask how to fix bicycles.
3. A **Secure Admin Dashboard** where fleet managers can view repair metrics, track inventory, and manage active support tickets.

---

## ✨ Implemented Functionalities

### 1. Student Ticketing Portal (`/`)
- **Issue Reporting:** A web form where users enter a Bike ID, select an issue type (e.g., Flat Tire, Brakes, Gears), and provide a description.
- **Auto-Provisioning:** If a user submits a ticket for a Bike ID that doesn't exist in the database, the backend automatically registers the new bike.
- **Animated UI:** Smooth success animations using Framer Motion when a ticket is submitted.

### 2. Public AI Repair Assistant (`/repair`)
- **RAG Chatbot:** An AI chatbot trained on bicycle maintenance manuals. It searches a local vector database to find relevant repair instructions.
- **Smart Query Handling:** The AI distinguishes between general questions (e.g., "How do I use a bike?") which it answers from internal knowledge, and technical repair questions which it answers strictly using the manuals to prevent hallucinations.

### 3. Secure Admin Dashboard (`/admin`)
- **Authentication:** The dashboard is protected by a login screen (`/admin/login`). It validates credentials against the backend API.
- **KPI Metrics:** Displays real-time data calculated by the backend:
  - **MTTR (Mean Time To Repair):** Average days taken to resolve a ticket.
  - **Open Tickets:** Total unresolved issues.
  - **Missed SLAs:** Tickets open for an extended period.
- **Inventory Monitoring:** Lists spare parts (e.g., Inner Tubes) and visually pulses red if the stock falls below the minimum threshold.
- **Work Order Charts:** An interactive bar chart (using Recharts) visualizing the distribution of ticket statuses (Open, In Progress, Resolved).
- **Ticket Management Table:** A complete list of all reported tickets. Admins can update a ticket's status via a dropdown, which instantly updates the database and recalculates the MTTR.

---

## 💻 Technologies & Stack

### Frontend (User Interface)
- **React & Vite:** Fast frontend framework and build tool.
- **Tailwind CSS (v4):** Used for styling and building the glassmorphic UI.
- **React Router:** Handles routing (`/`, `/repair`, `/admin`).
- **React Query:** Manages fetching data from the backend API.
- **Recharts:** Used for data visualization on the Admin Dashboard.
- **Framer Motion:** Used for UI animations.

### Backend (API & Database)
- **Python (FastAPI):** High-performance backend serving REST API endpoints.
- **SQLAlchemy:** Python ORM mapping data to the database.
- **SQLite:** The database used to store Bikes, Work Orders, and Inventory.
- **Pandas:** Used for aggregating data and calculating KPI metrics (like MTTR).

### AI & Retrieval-Augmented Generation (RAG)
- **LangChain:** Orchestrates the AI pipeline.
- **ChromaDB:** A local vector database that stores embedded text from the repair manuals.
- **HuggingFace (`all-MiniLM-L6-v2`):** The embedding model used to convert manual text into vectors for similarity search.
- **Groq API (`llama-3.1-8b-instant`):** The Large Language Model used to synthesize answers based on the retrieved context.
