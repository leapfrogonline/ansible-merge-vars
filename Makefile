default: test-all

deps:
	pipenv install

packaging-deps:
	pipenv install --dev

generate-tox-config: deps
	pipenv run python tests/bin/generate_tox_config.py

prep-release: generate-tox-config

lint:
	pipenv run tox -e lint

test-all: generate-tox-config 
	pipenv run detox

ci-test: deps
	pipenv run tox

clean:
	rm -rf .tox .hypothesis dist

build: clean packaging-deps
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel

pypi-test: build
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi: build
	pipenv run twine upload dist/*
