SHELL := /bin/bash

VENV_DIR = venv

ifeq ($(OS),Windows_NT)
	VENV_PYTHON = $(VENV_DIR)\Scripts\python.exe
	VENV_PIP = $(VENV_DIR)\Scripts\pip.exe
	DEL = rmdir /S /Q
else
	VENV_PYTHON = $(VENV_DIR)/bin/python
	VENV_PIP = $(VENV_DIR)/bin/pip
	DEL = rm -rf
endif

setup:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating new virtual environment..."; \
		python -m venv $(VENV_DIR); \
	else \
		echo "Using existing virtual environment..."; \
	fi

	$(VENV_PYTHON) -m pip install --upgrade pip setuptools wheel
	$(VENV_PYTHON) -m pip install -e ".[dev,bokeh,websockets]"

shell:
ifeq ($(OS),Windows_NT)
	@cmd /k "venv\Scripts\activate"
else
	@bash --rcfile <(echo "source venv/bin/activate")
endif

develop:
	pip install -e ".[dev,bokeh,websockets]"

build:
	$(VENV_PYTHON) -m build

test:
	pytest -v -s --log-cli-level=INFO

clean:
	$(DEL) build dist *.egg-info
ifeq ($(OS),Windows_NT)
	@for /d %%D in (.) do if exist "%%D\__pycache__" $(DEL) "%%D\__pycache__"
	@del /S /Q *.pyc 2>nul || true
else
	@find . -type d -name "__pycache__" -exec $(DEL) {} +
	@find . -name "*.pyc" -delete
endif

docs:
	cd docs && $(MAKE) html

lint:
	flake8 src tests
	mypy src

format:
	black src tests examples
	isort src tests examples
