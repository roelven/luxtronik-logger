const fs = require('fs');
const path = require('path');
const Papa = require('papaparse');
const luxtronik = require('luxtronik2');

const CFG = {
    hp_ip: process.env.LUXTRONIK_IP || '192.168.20.180',
    hp_port: parseInt(process.env.LUXTRONIK_PORT, 10) || 8889,
    data_dir: path.resolve(__dirname, '..', 'data'),
    out_file: path.resolve(__dirname, '..', 'data', 'live.dta.csv'),
};

// Promisify the read function for async/await
function readPump(pump) {
    return new Promise((resolve) => {
        pump.read((err, data) => {
            if (err) {
                console.error("Could not read from heat pump:", err);
                resolve(null);
            } else {
                resolve(data);
            }
        });
    });
}

async function main() {
    // Ensure the data directory exists
    fs.mkdirSync(CFG.data_dir, { recursive: true });

    const pump = luxtronik.createConnection(CFG.hp_ip, CFG.hp_port);
    const data = await readPump(pump);

    if (!data) {
        console.error("Exiting: Failed to get data from heat pump.");
        process.exit(1);
    }

    const now = new Date();
    const rowData = {
        Timestamp: Math.floor(now.getTime() / 1000),
        DateTime: now.toLocaleString('de-DE', { timeZone: 'Europe/Berlin' }),
        ...data.calculations,
        ...data.parameters,
    };

    let rows = [];
    let header = Object.keys(rowData); // Use keys from the first successful read as the header

    if (fs.existsSync(CFG.out_file)) {
        const fileContent = fs.readFileSync(CFG.out_file, 'utf-8');
        const parsed = Papa.parse(fileContent, { header: true, skipEmptyLines: true });
        rows = parsed.data;
        // Use existing header if file is not empty
        if (rows.length > 0) {
            header = Object.keys(rows[0]);
        }
    }

    // Add the new data
    rows.push(rowData);

    // Unparse the data back to a CSV string
    const csv = Papa.unparse(rows, {
        columns: header, // Ensure consistent column order
        header: true,
        delimiter: ';',
        newline: '\r\n',
    });

    // Write the entire file, overwriting it
    fs.writeFileSync(CFG.out_file, csv);

    console.log(`OK: Successfully wrote data to ${CFG.out_file} at ${now.toISOString()}`);
}

main();