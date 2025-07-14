# Luxtronik Logger (Node.js)

This project logs data from a Luxtronik heat pump controller and saves it to CSV files. This version uses Node.js.

## Data Collection and Frequency

Each time the script runs, it captures a **point-in-time snapshot** of the heat pump's current state, including all available calculations and parameters. It does not retrieve historical data; it only logs the values at the moment of execution.

A sensible frequency for data collection is **every 5 minutes**. This provides a good balance between data granularity for analysis and minimizing the load on the heat pump's controller. Running every 5 minutes will generate 288 data points per day.

## Setup

1.  Install Node.js (v18 or higher).
2.  Install dependencies: `npm install`

## Usage

-   To log data from the heat pump (this will also create the `header.json` on first run): `node src/index.js`
-   To create daily roll-ups: `node src/rollup.js`

## Docker

To build the Docker image:

```
docker build -t luxtronik-logger .
```

### Running the Logger Periodically

The container is designed to run, log the current data once, and then exit. To collect data continuously, you should use an external scheduler like `cron` on your host machine to run the container at a regular interval.

Here is an example `crontab` entry to run the logger every 5 minutes:

```sh
# Edit your crontab with: crontab -e
# Add the following line, replacing /path/to/your/project/data with the absolute path
*/5 * * * * docker run --rm -v /path/to/your/project/data:/app/data luxtronik-logger
```
*Note: On some systems (like Docker Desktop for Mac/Windows), you may need to add `--network="host"` or use other networking solutions if the container cannot reach your heat pump.*

### Triggering the Daily Rollup

The daily rollup script should be run once a day, preferably shortly after midnight, to process the previous day's logs. You can also use `cron` for this.

This command runs the `rollup.js` script inside a new container.

Here is an example `crontab` entry to run the rollup every day at 5 minutes past midnight:

```sh
# Edit your crontab with: crontab -e
# Add the following line, replacing /path/to/your/project/data with the absolute path
5 0 * * * docker run --rm -v /path/to/your/project/data:/app/data luxtronik-logger node src/rollup.js
```
