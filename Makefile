.PHONY: docker-up docker-down docker-reset airflow-init logs

# Spin up the entire containerized architecture in detached mode
docker-up:
	docker compose up -d

# Stop all containers and remove them
docker-down:
	docker compose down

# Destroy containers and remove all persistent volumes (Wipes Database!)
docker-reset:
	docker compose down -v
	@echo "All containers and volumes destroyed."

# Re-run the Airflow init script if needed
airflow-init:
	docker compose run --rm airflow-init

# View live logs of all services
logs:
	docker compose logs -f
