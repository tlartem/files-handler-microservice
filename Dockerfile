FROM python:3.12-alpine

WORKDIR /src

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock /src/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /src

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]