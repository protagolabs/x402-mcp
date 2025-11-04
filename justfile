# Justfile for MCP Server project
# https://github.com/casey/just

# Default recipe
default: help

# Install dependencies
install:
	pip install -r requirements.txt

# Install in development mode
develop:
	pip install -e .

# Run the server
run:
	python app.py

# Test the server
test:
	python test_server.py

# Show help
help:
	@echo "Available recipes:"
	@echo "  install    - Install dependencies"
	@echo "  develop    - Install in development mode"
	@echo "  run        - Run the server"
	@echo "  test       - Test the server"
	@echo "  help       - Show this help"
