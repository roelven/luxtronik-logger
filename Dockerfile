FROM python:3.10-slim

# Set the locale
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE:de
ENV LC_ALL de_DE.UTF-8

WORKDIR /app

COPY pyproject.toml .
COPY src src
COPY config config
COPY data data

RUN pip install .

# Generate the header file
RUN python src/csv-headers.py

CMD ["python", "src/licv_csv_dump.py"]