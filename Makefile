.PHONY: install test lint up

install:
	python -m pip install -r backend/requirements.txt
	npm --prefix frontend install

test:
	cd backend && python -m pytest
	npm --prefix frontend test

lint:
	ruff check src backend bot
	ruff format --check src backend bot
	npm --prefix frontend run lint

up:
	docker compose up --build
