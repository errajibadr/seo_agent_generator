# Makefile for SEO Agent Generator

# Variables
PYTHON = uv run
VENV_DIR = .venv
INPUT_DIR = data
OUTPUT_DIR = output
DEFAULT_CSV = $(INPUT_DIR)/
DEFAULT_MAX_CONCURRENT = 2
DEFAULT_BATCH = 2

# Define phony targets
.PHONY: all setup clean venv install help run_main run_batch run_image

# Default target
all: help

# Setup environment and dependencies
setup: venv install

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	uv venv $(VENV_DIR)

# Install dependencies
install:
	@echo "Installing dependencies..."
	uv pip install -e .

# Clean output directories
clean:
	@echo "Cleaning output directories..."
	rm -rf $(OUTPUT_DIR)/*

# Run main application with the default input
run_main:
	$(PYTHON) main.py --input $(DEFAULT_CSV) --output $(OUTPUT_DIR)

# Run main application in batch mode
# Usage: make run [BATCH=number] [MAX_CONCURRENT=number]
run:
	$(PYTHON) main.py --input $(INPUT_DIR) --output $(OUTPUT_DIR) --batch $(if $(BATCH),$(BATCH),$(DEFAULT_BATCH)) --max-concurrent $(if $(MAX_CONCURRENT),$(MAX_CONCURRENT),$(DEFAULT_MAX_CONCURRENT))

# Run the image API service
run_image:
	$(PYTHON) -m src.services.image_api_service

# Help information
help:
	@echo "Available commands:"
	@echo "  make setup       - Setup virtual environment and install dependencies"
	@echo "  make venv        - Create virtual environment only"
	@echo "  make install     - Install dependencies only"
	@echo "  make run_main    - Run the main application with the default CSV input"
	@echo "  make run_batch   - Run the main application in batch mode"
	@echo "  make run_image   - Run the image API service"
	@echo "  make clean       - Clean output directories" 