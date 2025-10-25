# Variables
VENV_NAME := .venv
PYTHON := python
REQUIREMENTS := requirements.txt

# Create virtual environment
venv:
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "✅ Virtual environment created in $(VENV_NAME)"

# Activate environment (manual step for terminal)
activate:
	@echo "Run this command to activate your environment:"
	@echo "source $(VENV_NAME)/bin/activate"

# Install dependencies
install:
	$(VENV_NAME)/bin/pip install -r $(REQUIREMENTS)
	@echo "✅ Requirements installed"

# Freeze requirements file
freeze:
	$(VENV_NAME)/bin/pip freeze > $(REQUIREMENTS)
	@echo "✅ Updated $(REQUIREMENTS)"

# One-shot setup
setup: venv install activate
	@echo "🚀 Environment setup complete!"
