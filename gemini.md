# Gemini Evaluation and Task List for Luxtronik Logger

## Evaluation

The project consists of a Python script (`licv_csv_dump.py`) that appears to process a proprietary data file (`.dta.csv`) from a Luxtronik heat pump controller and convert it into a standard CSV format. The script `csv-headers.py` and the JSON file `header.json` are used to generate the correct headers for the CSV file.

The code is currently a collection of scripts and would benefit from being structured as a proper Python project. This will make it more maintainable, testable, and easier to deploy.

## Task List

- [ ] Initialize a Git repository.
- [ ] Create a `gemini.md` file with an evaluation and task list.
- [ ] Structure the project as a proper Python project:
    - [ ] Create a `pyproject.toml` for project metadata and dependencies.
    - [ ] Use `venv` for a virtual environment.
    - [ ] Create a `src` directory for the main source code.
    - [ ] Move the scripts into the `src` directory.
    - [ ] Create a `tests` directory for unit tests.
- [ ] Run `licv_csv_dump.py` to test the application.
- [ ] Wrap the application in a Docker container.
- [ ] Analyze the data to determine the run frequency.
- [ ] Create daily roll-ups of the output.
