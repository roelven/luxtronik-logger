# Gemini Evaluation and Task List for Luxtronik Logger

## Evaluation

The project consists of a Python script (`licv_csv_dump.py`) that appears to process a proprietary data file (`.dta.csv`) from a Luxtronik heat pump controller and convert it into a standard CSV format. The script `csv-headers.py` and the JSON file `header.json` are used to generate the correct headers for the CSV file.

The code is currently a collection of scripts and would benefit from being structured as a proper Python project. This will make it more maintainable, testable, and easier to deploy.

## Task List

- [x] Initialize a Git repository.
- [x] Create a `gemini.md` file with an evaluation and task list.
- [x] Structure the project as a proper Python project:
    - [x] Create a `pyproject.toml` for project metadata and dependencies.
    - [x] Use `venv` for a virtual environment.
    - [x] Create a `src` directory for the main source code.
    - [x] Move the scripts into the `src` directory.
    - [x] Create a `tests` directory for unit tests.
- [x] Run `licv_csv_dump.py` to test the application.
- [x] Wrap the application in a Docker container.
- [x] Analyze the data to determine the run frequency.
- [x] Create daily roll-ups of the output.
