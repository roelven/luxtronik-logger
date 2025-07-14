# Luxtronik Logger (Node.js)

This project logs data from a Luxtronik heat pump controller and saves it to CSV files using a Docker container.

## Data Collection and Frequency

Each time the container runs, it captures a **point-in-time snapshot** of the heat pump's current state, including all available calculations and parameters. It does not retrieve historical data; it only logs the values at the moment of execution.

A sensible frequency for data collection is **every 5 minutes**. This provides a good balance between data granularity for analysis and minimizing the load on the heat pump's controller. Running every 5 minutes will generate 288 data points per day.

## Docker Usage

### Build the Image

First, build the Docker image:
```
docker build -t luxtronik-logger .
```

### Running the Logger Periodically

The container is designed to run, log the current data once, and then exit. To collect data continuously, you should use an external scheduler like `cron` on your host machine to run the container at a regular interval.

You can configure the heat pump's IP address and port using environment variables.

-   `LUXTRONIK_IP`: The IP address of your heat pump (defaults to `192.168.20.180`).
-   `LUXTRONIK_PORT`: The port for the controller (defaults to `8889`).

Here is an example `crontab` entry to run the logger every 5 minutes, overriding the default IP. **Note:** You must replace `/path/to/your/project/data` with the absolute path to this project's `data` directory on your machine.

```sh
# Edit your crontab with: crontab -e
*/5 * * * * docker run --rm -e LUXTRONIK_IP=192.168.1.100 -v /path/to/your/project/data:/app/data luxtronik-logger
```
*On some systems (like Docker Desktop for Mac/Windows), you may need to add `--network="host"` or other networking solutions if the container cannot reach your heat pump.*

### Triggering the Daily Rollup

The daily rollup script should be run once a day, preferably shortly after midnight, to process the previous day's logs. You can also use `cron` for this.

This command runs the `rollup.js` script inside a new container.

Here is an example `crontab` entry to run the rollup every day at 5 minutes past midnight. **Note:** Remember to use the correct absolute path to your `data` directory.

```sh
# Edit your crontab with: crontab -e
5 0 * * * docker run --rm -v /path/to/your/project/data:/app/data luxtronik-logger node src/rollup.js
```
