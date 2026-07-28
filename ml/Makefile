PYTHON ?= python3.10
VENV ?= .venv
BIN := $(VENV)/bin
DATASET_DIR ?= ../Datasets

.PHONY: setup test lint check stages doctor inventory eda clean-data resolve-entities annotation-sample silver-annotate snapshot clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/pip install -r requirements-dev.lock.txt
	$(BIN)/pip install --no-deps -e .

test:
	$(BIN)/pytest

lint:
	$(BIN)/ruff check src tests

check: lint test

stages:
	$(BIN)/sipature-ml stages

doctor:
	$(BIN)/sipature-ml doctor

inventory:
	$(BIN)/sipature-ml run inventory --dataset-dir "$(DATASET_DIR)"

eda:
	$(BIN)/sipature-ml run eda --dataset-dir "$(DATASET_DIR)"

clean-data:
	$(BIN)/sipature-ml run clean --dataset-dir "$(DATASET_DIR)"

resolve-entities:
	$(BIN)/sipature-ml run resolve-entities

annotation-sample:
	$(BIN)/sipature-ml annotation-sample

silver-annotate:
	$(BIN)/sipature-ml silver-annotate

snapshot:
	$(BIN)/sipature-ml snapshot-run --output artifacts/reports/run-environment.json

clean:
	rm -rf .pytest_cache .ruff_cache build dist src/*.egg-info src/sipature_ml/__pycache__ tests/__pycache__
