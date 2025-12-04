IMAGE_NAME = trellis-app
CONTAINER_NAME = trellis-container
PORT ?= 8000

.PHONY: help build run stop test clean curl-tests start-server stop-server integration-test

# Default target - show help
help:
	@echo "Trellis Number Converter - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Development:"
	@echo "  make start-server     Start Django dev server (PORT=$(PORT))"
	@echo "  make stop-server      Stop running dev server"
	@echo "  make test             Run Django unit tests"
	@echo "  make curl-tests       Run 102 curl tests against running server"
	@echo "  make integration-test Full cycle: start server, run curls, stop"
	@echo ""
	@echo "Docker:"
	@echo "  make build            Build Docker image"
	@echo "  make run              Build and run Docker container"
	@echo "  make stop             Stop Docker container"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove cache files and stop containers"
	@echo ""
	@echo "Configuration:"
	@echo "  PORT=8001 make <cmd>  Override default port (default: 8000)"
	@echo ""
	@echo "Examples:"
	@echo "  make start-server              # Start on port 8000"
	@echo "  PORT=8001 make start-server    # Start on port 8001"
	@echo "  PORT=8001 make curl-tests      # Test against port 8001"
	@echo ""

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run --rm -p $(PORT):8000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	@docker stop $(CONTAINER_NAME) 2>/dev/null || echo "Container not running"

test: build
	docker run --rm $(IMAGE_NAME) python manage.py test api.tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true

# Start the development server in the background
start-server:
	@echo "Starting server on port $(PORT)..."
	@python manage.py runserver $(PORT) &
	@sleep 2
	@echo "Server started on http://localhost:$(PORT)"

# Stop any running development server
stop-server:
	@pkill -f "manage.py runserver" 2>/dev/null || true
	@echo "Server stopped"

# Run curl tests against all numbers in test_numbers.txt
curl-tests:
	@echo "Running curl tests against http://localhost:$(PORT)/num_to_english"
	@echo "==========================================================="
	@passed=0; failed=0; total=0; \
	while IFS= read -r number || [ -n "$$number" ]; do \
		total=$$((total + 1)); \
		response=$$(curl -s "http://localhost:$(PORT)/num_to_english?number=$$number"); \
		status=$$(echo "$$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null); \
		if [ "$$status" = "ok" ]; then \
			result=$$(echo "$$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('num_in_english',''))" 2>/dev/null); \
			echo "✓ $$number → $$result"; \
			passed=$$((passed + 1)); \
		else \
			echo "✗ $$number → FAILED: $$response"; \
			failed=$$((failed + 1)); \
		fi; \
	done < test_numbers.txt; \
	echo "==========================================================="; \
	echo "Results: $$passed passed, $$failed failed, $$total total"

# Run full integration test: start server, run curls, stop server
integration-test: stop-server start-server
	@sleep 1
	@$(MAKE) curl-tests PORT=$(PORT)
	@$(MAKE) stop-server
