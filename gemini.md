# Gemini Evaluation and Task List for Luxtronik Logger

## Evaluation

The project consists of a script that processes data from a Luxtronik heat pump controller and converts it into a standard CSV format.

The initial Python implementation faced insurmountable issues with the `Bouni/python-luxtronik` library within the Docker environment. Despite the container having network access, the library failed to connect.

The project has been pivoted to a Node.js implementation using the `coolchip/luxtronik2` library, which is expected to be more reliable in a containerized environment.

## Task List

- [x] Initialize a Git repository.
- [x] Create a `gemini.md` file with an evaluation and task list.
- [x] Structure the project as a proper Python project.
- [x] **Pivot to Node.js due to Python library issues.**
- [x] Initialize a Node.js project.
- [x] Implement data dumping and CSV generation in Node.js.
- [x] Implement daily roll-ups in Node.js.
- [x] Create a Node.js-based Dockerfile.
- [x] Update the README.
- [ ] Verify the Node.js implementation.
- [ ] Analyze the data to determine the run frequency.
- [ ] Create daily roll-ups of the output.
