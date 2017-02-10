PYTHON := env/bin/python
PIP := env/bin/pip
PYLINT := env/bin/pylint

default: test-all

.build-timestamps:
	mkdir .build-timestamps

env:
	virtualenv --no-site-packages --python python2.7 env

.build-timestamps/packaging-deps: requirements/packaging.txt env | .build-timestamps
	$(PIP) install -U -r requirements/packaging.txt
	touch $@

.build-timestamps/dev-deps: .build-timestamps/packaging-deps requirements/dev.txt env | .build-timestamps
	$(PIP) install -U -r requirements/dev.txt
	touch $@

packaging-deps: $(ENV) .build-timestamps/packaging-deps
dev-deps: $(ENV) .build-timestamps/dev-deps

lint: .build-timestamps/dev-deps
	$(PYLINT) merge_vars.py tests

test: .build-timestamps/dev-deps
	$(PYTHON) -m unittest discover -s tests

examples: .build-timestamps/dev-deps
	env/bin/ansible-playbook examples/*_playbook.yml

test-all: lint test examples

clean:
	rm -rf env
	rm -rf .build-timestamps

.PHONY: default clean test packaging-deps dev-deps lint test-all examples
