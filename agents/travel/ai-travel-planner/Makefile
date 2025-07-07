.PHONY: install start backend frontend clean test format lint help

# Default target
help:
	@echo "AI Travel Planner - Available Commands:"
	@echo ""
	@echo "  make install     - Install all dependencies (Python + npm)"
	@echo "  make start       - Start both backend and frontend"
	@echo "  make backend     - Start only backend server"
	@echo "  make frontend    - Start only frontend server"
	@echo "  make test        - Run tests"
	@echo "  make format      - Format code with black"
	@echo "  make lint        - Run linting checks"
	@echo "  make clean       - Clean cache and temporary files"
	@echo ""

# Install all dependencies
install:
	@echo "Installing Python dependencies with Poetry..."
	poetry install
	@echo "Installing frontend dependencies..."
	cd frontend/trip-planner && npm install
	@echo "✅ All dependencies installed!"

# Start both services
start:
	@./bootstrap.sh

# Start only backend
backend:
	@echo "Starting backend server..."
	poetry run python -m backend.main

# Start only frontend
frontend:
	@echo "Starting frontend server..."
	cd frontend/trip-planner && npm run dev

# Run tests
test:
	@echo "Running tests..."
	poetry run pytest

# Format code
format:
	@echo "Formatting code with black..."
	poetry run black .
	@echo "✅ Code formatted!"

# Run linting
lint:
	@echo "Running flake8..."
	poetry run flake8 .
	@echo "Running mypy..."
	poetry run mypy .
	@echo "✅ Linting complete!"

# Clean cache and temporary files
clean:
	@echo "Cleaning cache and temporary files..."
	poetry cache clear pypi --all
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd frontend/trip-planner && rm -rf node_modules/.cache
	@echo "✅ Cleanup complete!"