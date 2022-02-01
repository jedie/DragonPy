SHELL := /bin/bash
MAX_LINE_LENGTH := 119
POETRY_VERSION := $(shell poetry --version 2>/dev/null)

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-poetry:
	@if [[ "${POETRY_VERSION}" == *"Poetry"* ]] ; \
	then \
		echo "Found ${POETRY_VERSION}, ok." ; \
	else \
		echo 'Please install poetry first, with e.g.:' ; \
		echo 'make install-poetry' ; \
		exit 1 ; \
	fi

install-poetry: ## install or update poetry
	@if [[ "${POETRY_VERSION}" == *"Poetry"* ]] ; \
	then \
		echo 'Update poetry v$(POETRY_VERSION)' ; \
		poetry self update ; \
	else \
		echo 'Install poetry' ; \
		curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" | python3 ; \
	fi

install: check-poetry ## install DragonPy via poetry
	poetry install

update: check-poetry ## Update the dependencies as according to the pyproject.toml file
	poetry update

lint: ## Run code formatters and linter
	poetry run darker --check

fix-code-style: ## Fix code formatting
	poetry run darker

tox-listenvs: check-poetry ## List all tox test environments
	poetry run tox --listenvs

tox: check-poetry ## Run pytest via tox with all environments
	poetry run tox

tox-py36: check-poetry ## Run pytest via tox with *python v3.6*
	poetry run tox -e py36

tox-py37: check-poetry ## Run pytest via tox with *python v3.7*
	poetry run tox -e py37

tox-py38: check-poetry ## Run pytest via tox with *python v3.8*
	poetry run tox -e py38

pytest: check-poetry ## Run pytest
	poetry run pytest

update-rst-readme: ## update README.rst from README.creole
	poetry run update_rst_readme

publish: ## Release new version to PyPi
	poetry run publish

profile:  ## Profile the MC6809 emulation benchmark
	poetry run MC6809 profile

benchmark:  ## Run MC6809 emulation benchmark
	poetry run MC6809 benchmark

editor: check-poetry  ## Run only the BASIC editor
	poetry run devshell editor

Vectrex: check-poetry  ## Run GUI with Vectrex emulation (not working, yet!)
	poetry run devshell run --machine Vectrex

sbc09: check-poetry  ## Run GUI with sbc09 ROM emulation
	poetry run devshell run --machine sbc09

Multicomp6809: check-poetry  ## Run GUI with Multicomp6809 ROM emulation
	poetry run devshell run --machine Multicomp6809

Simple6809: check-poetry  ## Run GUI with Simple6809 ROM emulation
	poetry run devshell run --machine Simple6809

CoCo2b: check-poetry  ## Run GUI with CoCo 2b emulation
	poetry run devshell run --machine CoCo2b

Dragon32: check-poetry  ## Run GUI with Dragon 32 emulation
	poetry run devshell run --machine Dragon32

Dragon64: check-poetry  ## Run GUI with Dragon 64 emulation
	poetry run devshell run --machine Dragon64

run: check-poetry ## *Run the DragonPy Emulator GUI*
	poetry run devshell gui

.PHONY: help install lint fix test publish