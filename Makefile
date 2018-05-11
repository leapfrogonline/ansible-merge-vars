default: generate-tox-config test-all

deps:
	pipenv install

generate-tox-config: deps
	pipenv run python bin/generate_tox_config.py

prep-release: generate-tox-config

lint:
	pipenv run tox -e lint

test-all:
	pipenv run detox

ci-test: deps
	pipenv run detox
# ci-test: deps
#         pipenv run tox

clean:
	rm -rf .tox .hypothesis
