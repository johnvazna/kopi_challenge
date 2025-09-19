.PHONY: help install test run down clean logs build restart status shell redis-cli

help: ## List available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed successfully"

test: ## Run tests
	@echo "Running tests..."
	python -m pytest tests/ -v
	@echo "Tests completed"

run: ## Start API + Redis with Docker
	@echo "Starting services with Docker Compose..."
	docker-compose up -d
	@echo "Services started"
	@echo "API available at: http://localhost:8000"
	@echo "Redis available at: localhost:6379"

down: ## Stop services
	@echo "Stopping services..."
	docker-compose down
	@echo "Services stopped"

clean: ## Stop and remove containers/volumes
	@echo "Cleaning completely..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "Containers and volumes removed"

logs: ## Show service logs
	docker-compose logs -f

build: ## Build Docker image
	docker-compose build

restart: ## Restart services
	docker-compose restart

status: ## Show service status
	docker-compose ps

shell: ## Open shell in API container
	docker-compose exec api bash

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli
