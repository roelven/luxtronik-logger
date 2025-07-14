const fs = require('fs');
const path = require('path');
const Papa = require('papaparse');

const projectRoot = path.resolve(__dirname, '..');
const dataDir = path.join(projectRoot, 'data');

const liveFile = path.join(dataDir, 'live.dta.csv');
const today = new Date();
const yesterday = new Date(today);
yesterday.setDate(yesterday.getDate() - 1);
const yesterdayISO = yesterday.toISOString().split('T')[0];
const rollupFile = path.join(dataDir, `${yesterdayISO}.csv`);

if (fs.existsSync(liveFile)) {
    const csvData = fs.readFileSync(liveFile, 'utf-8');
    const { data: rows, meta } = Papa.parse(csvData, { header: true, skipEmptyLines: true });

    const yesterdayRows = [];
    const remainingRows = [];

    rows.forEach(row => {
        // Assuming DateTime is in a format that can be parsed by new Date()
        // e.g., "14.07.2025, 13:40:00"
        const [datePart, timePart] = row.DateTime.split(', ');
        const [day, month, year] = datePart.split('.');
        const formattedDate = `${year}-${month}-${day}T${timePart}`;
        const rowDate = new Date(formattedDate);

        if (rowDate.toISOString().startsWith(yesterdayISO)) {
            yesterdayRows.push(row);
        } else {
            remainingRows.push(row);
        }
    });

    if (yesterdayRows.length > 0) {
        const rollupCsv = Papa.unparse(yesterdayRows, { header: true, delimiter: ';', newline: '\r\n' });
        fs.writeFileSync(rollupFile, rollupCsv);
        console.log(`Created rollup file: ${rollupFile}`);
    }

    if (remainingRows.length > 0) {
        const remainingCsv = Papa.unparse(remainingRows, { header: true, delimiter: ';', newline: '\r\n' });
        fs.writeFileSync(liveFile, remainingCsv);
    } else {
        // If all rows were from yesterday, the live file becomes empty
        fs.unlinkSync(liveFile);
    }
}
