.PHONY: demo clean

demo:
	@echo "🚴 Starting UniBike Analytics Demo..."
	@echo "1. Generating sample PDF repair manuals..."
	python3 src/scripts/generate_pdfs.py || echo "Warning: Could not generate PDFs locally, ensure fpdf2 is installed or run inside docker."
	
	@echo "2. Building and starting Docker containers..."
	docker-compose up --build -d
	
	@echo "3. Waiting for PostgreSQL and App to initialize..."
	sleep 10
	
	@echo "4. Seeding the database with mock data..."
	docker-compose exec app python src/database/seeder.py
	
	@echo "5. Starting inventory alert background script..."
	# Run it in detached mode inside the container
	docker-compose exec -d app python src/scripts/inventory_alert.py
	
	@echo "✅ Demo is live! Access the application at: http://localhost:7860"
	@echo "Admin credentials -> Username: admin | Password: password"

clean:
	@echo "🧹 Cleaning up resources..."
	docker-compose down -v
	rm -rf data/chroma
	rm -f data/*.pdf
	@echo "Clean complete."
