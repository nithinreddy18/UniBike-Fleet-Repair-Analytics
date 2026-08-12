# 🛠️ Setup Guide for UniBike Analytics

If you have just cloned or downloaded this repository, follow these instructions step-by-step to run the entire full-stack application perfectly on your local machine.

## 📋 Prerequisites
Ensure you have the following installed on your machine:
- **Python (3.9 or higher)**
- **Node.js (18 or higher) and npm**
- A **Groq API Key** (You can get one for free at [console.groq.com](https://console.groq.com))

---

## 1️⃣ Set up the Python Backend

The backend is a FastAPI application that handles the database and AI Logic.

1. Open a terminal and navigate to the root folder of the project:
   ```bash
   cd "UniBike Fleet & Repair Analytics"
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install all required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root folder and add your Groq API key. This is **required** for the AI Repair Assistant to function.
   ```env
   GROQ_API_KEY=gsk_your_api_key_here
   ```

5. Seed the database. This script creates the local SQLite database (`data/unibike.db`) and populates it with sample bikes, work orders, and inventory:
   ```bash
   PYTHONPATH=. python src/database/seeder.py
   ```

6. Start the backend server:
   ```bash
   PYTHONPATH=. uvicorn src.api.server:app --host 0.0.0.0 --port 8000
   ```
   *Leave this terminal window running.*

---

## 2️⃣ Set up the React Frontend

The frontend is a React Single Page Application built with Vite.

1. Open a **new** terminal window and navigate to the `frontend` folder:
   ```bash
   cd "UniBike Fleet & Repair Analytics/frontend"
   ```

2. Install the Node modules:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Leave this terminal window running.*

---

## 3️⃣ Run and Test the Application

Open your web browser and navigate to **[http://localhost:5173](http://localhost:5173)**.

### Testing the Features:
1. **Report a Bike (Home Page):** Try filling out the form on the homepage to report a broken bike.
2. **AI Repair Assistant (`/repair`):** Click "Repair Assistant" in the navigation bar. Ask a question like *"How do I fix a flat tire?"* to test the AI. (Note: The first question might take a few seconds as the vector database initializes).
3. **Admin Dashboard (`/admin`):** Click "Admin Dashboard" in the navigation bar. 
   - You will be prompted to log in. 
   - **Username:** `admin`
   - **Password:** `password`
   - Once logged in, you can view the KPI metrics, interactive charts, and manage the repair tickets in the table by changing their statuses.
