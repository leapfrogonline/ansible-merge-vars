PYTHON := $(VIRTUAL_ENV)/bin/python
PIP := $(VIRTUAL_ENV)/bin/pip
PYLINT := $(VIRTUAL_ENV)/bin/pylint

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))

default: test-all

dev-deps: requirements/dev.txt env
	$(PIP) install -U -r requirements/dev.txt

lint: dev-deps
	$(PYLINT) merge_vars.py tests

test: dev-deps
	$(PYTHON) -m unittest discover -s tests

examples: dev-deps
	env/bin/ansible-playbook -v examples/*_playbook.yml

test-all: lint test examples

clean:
	rm -rf env ci-env
	rm -rf .build

.PHONY: default clean test packaging-deps dev-deps lint test-all examples
