.PHONY: build test serve

build:
	python src/pipeline.py

test:
	pytest -q

serve:
	python -m http.server 8000 -d docs
