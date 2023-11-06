install:
	poetry install


dev:
	poetry run flask --app page_analyzer:app run


PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:8000 page_analyzer:app


