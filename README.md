# Luxtronik Logger (Node.js)

This project logs data from a Luxtronik heat pump controller and saves it to CSV files.

## Data Collection and Frequency

Each time the script runs, it captures a **point-in-time snapshot** of the heat pump's current state. A sensible frequency for data collection is **every 5 minutes**.

## Setup and Usage

This project is designed to be run directly on a host with Node.js, scheduled with `cron`.

### 1. Install Prerequisites

On your host machine (e.g., your server), install Node.js and npm:
```sh
sudo apt-get update && sudo apt-get install -y nodejs npm
```

### 2. Install Application Dependencies

Clone the repository and install the necessary Node.js packages:
```sh
# Clone the repository (if you haven't already)
# git clone https://github.com/roelven/luxtronik-logger.git

cd luxtronik-logger
npm install
```

### 3. Configure Environment Variables

The script is configured using environment variables. You can set these in your `crontab` file.

-   `LUXTRONIK_IP`: The IP address of your heat pump.
-   `LUXTRONIK_PORT`: The port for the controller (defaults to `8889`).

### 4. Schedule with Cron

Use `crontab -e` to set up the automated jobs.

**Note:** Replace `/path/to/luxtronik-logger` with the absolute path to where you cloned the project.

```sh
# Edit your crontab with: crontab -e

# Run the data logger every 5 minutes
*/5 * * * * cd /path/to/luxtronik-logger && export LUXTRONIK_IP=192.168.20.180 && /usr/bin/node src/index.js

# Run the daily rollup at 5 minutes past midnight
5 0 * * * cd /path/to/luxtronik-logger && /usr/bin/node src/rollup.js
```
