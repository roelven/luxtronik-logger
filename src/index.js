const fs = require('fs');
const path = require('path');
const Papa = require('papaparse');
const luxtronik = require('luxtronik2');

const projectRoot = path.resolve(__dirname, '..');
const configDir = path.join(projectRoot, 'config');
const dataDir = path.join(projectRoot, 'data');

const CFG = {
    hp_ip: process.env.LUXTRONIK_IP || '192.168.20.180',
    hp_port: parseInt(process.env.LUXTRONIK_PORT, 10) || 8889,
    header_file: path.join(configDir, 'header.json'),
    out_file: path.join(dataDir, 'live.dta.csv'),
};

// Ensure directories exist
if (!fs.existsSync(configDir)) fs.mkdirSync(configDir, { recursive: true });
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });

// Promisify the read function
function readPump(pump) {
    return new Promise((resolve, reject) => {
        pump.read((err, data) => {
            if (err) {
                return reject(err);
            }
            resolve(data);
        });
    });
}

async function main() {
    const pump = luxtronik.createConnection(CFG.hp_ip, CFG.hp_port);

    try {
        const data = await readPump(pump);
        const calculations = data.calculations;
        const parameters = data.parameters;

        // First, let's create the header file if it doesn't exist
        if (!fs.existsSync(CFG.header_file)) {
            const allKeys = [
                'Timestamp',
                'DateTime',
                ...Object.keys(calculations),
                ...Object.keys(parameters),
            ];
            fs.writeFileSync(CFG.header_file, JSON.stringify(allKeys));
        }

        const header = JSON.parse(fs.readFileSync(CFG.header_file, 'utf-8'));

        const now = new Date();
        const rowData = {
            Timestamp: Math.floor(now.getTime() / 1000),
            DateTime: now.toLocaleString('de-DE', { timeZone: 'Europe/Berlin' }),
            ...calculations,
            ...parameters,
        };

        // Ensure all header columns are present in the row
        const row = header.reduce((acc, key) => {
            acc[key] = rowData[key] !== undefined ? rowData[key] : '';
            return acc;
        }, {});

        const fileExists = fs.existsSync(CFG.out_file);

        // Use Papa.unparse to generate the CSV string for the new row
        // The `header` option is only true if the file does NOT exist
        const csv = Papa.unparse([row], {
            header: !fileExists,
            delimiter: ';',
            newline: '\r\n',
        });

        // Append the new CSV data (with or without header) to the file
        // We add an extra newline if the file already exists to ensure separation
        fs.appendFileSync(CFG.out_file, (fileExists ? '\n' : '') + csv);

        console.log(`OK ${CFG.out_file} ${now.toISOString()}`);

    } catch (error) {
        console.error(`Error connecting to heat pump: ${error.message}`);
        process.exit(1);
    }
}

main();
