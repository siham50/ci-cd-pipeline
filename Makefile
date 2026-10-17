up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f

test:
	cd app && pytest tests/ -v

lint:
	cd app && flake8 . --max-line-length=100

rebuild:
	docker compose up -d --build api