# Makefile

.PHONY: sdist publish install

sdist:
	@echo "Building source distribution..."
	python3 setup.py sdist

publish: sdist
	@echo "Publishing to pypi..."
	twine upload dist/*
	rm -rf dist

install:
	@echo "Installing..."
	python3 -m pip install .