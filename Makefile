.PHONY: setup run test lint clean

setup:
	# TODO(phase-1): Create a virtual environment and install dependencies.
	python -m pip install -r requirements.txt

run:
	# TODO(phase-2): Execute the configured pipeline workflow.
	python pipeline.py

test:
	# TODO(phase-1): Expand tests as implementation begins.
	pytest

lint:
	# TODO(phase-11): Add ruff, black, or another agreed quality tool.
	python -m compileall .

clean:
	# TODO(phase-11): Add safe cleanup for generated runtime artifacts.
	python scripts/setup_project.py --check
