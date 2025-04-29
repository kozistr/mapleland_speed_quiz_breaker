.PHONY: init format check requirements

init:
	python -m pip install -q -U poetry isort black ruff
	python -m poetry install --dev

format:
	isort --profile black -l 119 sqb
	black -S -l 119 sqb

check:
	black -S -l 119 --check sqb
	ruff check sqb

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev
