.PHONY: setup test run docker-up docker-down docker-reset airflow airflow-init spark dashboard clean lint logs

# ---------------------------------------------------------
# Developer Experience (DevEx) Commands
# ---------------------------------------------------------

setup:
	@echo "Setting up environment..."
	pip install -r requirements.txt
	python scripts/setup_project.py

test:
	@echo "Running tests..."
	pytest tests/ -v

run:
	@echo "Running local pipeline..."
	python scripts/run_pipeline_locally.py

dashboard:
	@echo "Starting Streamlit Dashboard..."
	streamlit run dashboard/app.py

clean:
	@echo "Cleaning up temp files and caches..."
	rm -rf .pytest_cache .pytest_tmp __pycache__ */__pycache__ data/processed/* data/exports/* logs/*.log

lint:
	@echo "Running code formatters and linters..."
	black .
	isort .
	flake8 .

# ---------------------------------------------------------
# Docker Containerization Commands
# ---------------------------------------------------------

docker-up:
	@echo "Starting Docker containers..."
	docker compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker compose down

docker-reset:
	@echo "Destroying containers and wiping PostgreSQL volumes..."
	docker compose down -v

# ---------------------------------------------------------
# Integrations Commands
# ---------------------------------------------------------

airflow-init:
	@echo "Initializing Airflow database..."
	docker compose run --rm airflow-init

airflow:
	@echo "Airflow runs inside docker. Check http://localhost:8080"

spark:
	@echo "Spark jobs can be executed locally or via spark-submit"
	python spark/spark_transformation.py

logs:
	docker compose logs -f
