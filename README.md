# Luxtronik Logger

This project logs data from a Luxtronik heat pump controller and saves it to CSV files.

## Setup

1.  Create a virtual environment: `python3 -m venv .venv`
2.  Activate the virtual environment: `source .venv/bin/activate`
3.  Install the dependencies: `pip install .`

## Usage

-   To generate the `header.json` file (only needs to be done once): `python src/csv-headers.py`
-   To log data from the heat pump: `python src/licv_csv_dump.py`
-   To create daily roll-ups: `python src/rollup.py`

## Docker

To build the Docker image:

```
docker build -t luxtronik-logger .
```

To run the Docker container:

```
docker run -v $(pwd)/data:/app/data luxtronik-logger
```
