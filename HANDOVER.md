# AStA Mobility Department Handover Guide

Welcome to the **UniBike Fleet & Repair Analytics** open-source repository! This system is designed as a turnkey solution to help manage the university's shared and secondhand bicycles.

## System Adoption

### 1. Generating QR Codes
To map physical bikes to the database, you need QR codes that point to the ticketing system.
- Deploy this application to a public domain (e.g., `https://bikes.asta.tu-darmstadt.de`).
- Generate QR codes containing the URL with the `bike_id` parameter. Unfortunately, Gradio Blocks does not easily read URL parameters dynamically on initialization without custom routing, so users may have to manually enter the `Bike ID` printed on the sticker, or you can host a small reverse proxy (like Nginx) that redirects `?bike_id=X` to a pre-filled endpoint.
- Attach the physical QR codes/stickers prominently on the bike frames.

### 2. Updating PDF Manuals
The DIY Repair Assistant uses RAG (Retrieval-Augmented Generation) on PDF manuals in the `data/` folder.
- To swap manuals, simply delete the existing PDFs in the `data/` directory and upload your official AStA repair manuals.
- Delete the `data/chroma/` directory to clear the old vector index.
- Restart the application (`docker-compose restart app`). The system will automatically ingest the new PDFs on startup.

### 3. Power BI Integration
A Power BI template placeholder is provided in `bi_templates/`.
- Open Power BI Desktop.
- Connect to the PostgreSQL database (`unibike_db`).
- Configure visuals for Mean Time to Repair (MTTR) and low spare-parts inventory.
- Save as `.pbix` and distribute to department admins.

### 4. Customizing the AI Model
By default, this project uses a lightweight local model (`google/flan-t5-small`) to remain fully open-source and run on standard CPUs. If you deploy this on a server with a GPU, or if you wish to use OpenAI/Gemini APIs for better responses, update `src/api/rag_chain.py` to point to your desired LLM integration via LangChain.
