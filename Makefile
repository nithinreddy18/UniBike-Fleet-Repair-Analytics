.PHONY: demo test build-frontend run-local dev-frontend docker-demo clean

test:
	@echo "🧪 Running full test suite..."
	PYTHONPATH=. ./venv/bin/pytest -v

build-frontend:
	@echo "⚛️ Building React Vite frontend..."
	cd frontend && npm install && npm run build

run-local: build-frontend
	@echo "🚀 Starting UniBike Unified Server on http://localhost:8000..."
	PYTHONPATH=. ./venv/bin/uvicorn src.api.server:app --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "💻 Starting Vite Dev Server on http://localhost:5173..."
	cd frontend && npm run dev

demo: build-frontend
	@echo "🚴 Starting UniBike Analytics Demo..."
	@echo "1. Generating sample PDF repair manuals..."
	PYTHONPATH=. ./venv/bin/python3 src/scripts/generate_pdfs.py || echo "Warning: Could not generate PDFs locally."
	@echo "2. Seeding database..."
	PYTHONPATH=. ./venv/bin/python3 src/database/seeder.py || echo "Database already seeded."
	@echo "3. Starting server on http://localhost:8000..."
	PYTHONPATH=. ./venv/bin/uvicorn src.api.server:app --host 0.0.0.0 --port 8000

docker-demo:
	@echo "🐳 Starting Docker containers..."
	docker compose up --build -d
	@echo "Waiting for app to initialize..."
	sleep 10
	docker compose exec app python src/database/seeder.py
	@echo "✅ Demo is live at: http://localhost:8000"

clean:
	@echo "🧹 Cleaning up resources..."
	rm -rf data/chroma
	rm -f data/*.pdf
	rm -rf frontend/dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Clean complete."
