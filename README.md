# Luxtronik Logger (Node.js)

This project logs data from a Luxtronik heat pump controller and saves it to CSV files. This version uses Node.js.

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

To run the Docker container:

```
# Note: You may need to use --network="host" on Linux systems
# if the heatpump is not discoverable otherwise.
docker run --rm -v "$(pwd)/data:/app/data" luxtronik-logger
```