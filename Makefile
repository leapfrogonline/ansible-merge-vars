VENV := venv
PIP := ./$(VENV)/bin/pip
PYTHON := ./$(VENV)/bin/python
TOX := ./$(VENV)/bin/tox
TWINE := ./$(VENV)/bin/twine

default: test-all

venv:
	python -m venv $(VENV)

dev-deps: venv
	$(PIP) install -U -r requirements.txt

generate-tox-config: dev-deps
	$(PYTHON) tests/bin/generate_tox_config.py

prep-release: generate-tox-config

lint: dev-deps generate-tox-config
	$(TOX) -e lint

test-all: dev-deps generate-tox-config 
	$(TOX) --parallel auto

clean:
	rm -rf venv .tox .hypothesis dist tox.ini

build: clean dev-deps
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel

pypi-test: build
	$(TWINE) upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi: build
	$(TWINE) upload dist/*
