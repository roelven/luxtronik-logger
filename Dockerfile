FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
COPY src src

RUN pip install .

CMD ["python", "src/licv_csv_dump.py"]
