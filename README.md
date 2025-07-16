# Luxtronik Data Logger

This project provides a Python-based data logger for Luxtronik-controlled heat pumps. It runs as a continuous daemon, collecting data at a configurable interval and saving it to a daily CSV file.

## Features

-   **Continuous Logging:** Runs as a background service to log data 24/7.
-   **Resilient:** Recovers from crashes by saving data to a temporary cache file.
-   **Daily CSV Roll-ups:** Automatically generates a new CSV file every day with the previous 24 hours of data.
-   **Configurable:** Logging interval and CSV generation time can be easily configured.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd luxtronik-logger
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the logger:**
    -   Copy the sample environment file:
        ```bash
        cp .env.sample .env
        ```
    -   Open the `.env` file and edit the `HOST` variable to your heat pump's IP address.

4.  **Configure the data mapping:**
    -   The `config/header-mapping-int.json` file maps the integer keys from the `python-luxtronik` library to the headers in the output CSV file. You can edit this file to add or change mappings.

## Usage

### Running the Daemon

To run the logger as a background process, you can use `nohup`:

```bash
nohup python3 src/logger_daemon.py &
```

The logger will run in the background and log any output to `data/daemon.log`.

### Generating a CSV Manually

You can manually trigger a CSV generation from the cached data by running:

```bash
python3 src/logger_daemon.py generate
```

This will create a new CSV file in the `data` directory and clear the cache.