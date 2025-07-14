#!/usr/bin/env python3
# licv_csv_dump.py 
import csv, datetime as dt, json, pathlib, locale
from luxtronik import Luxtronik                     # pip install luxtronik

# Determine the project root directory
project_root = pathlib.Path(__file__).parent.parent

CFG = {
    "hp_ip":   "192.168.20.180",
    "hp_port": 8889,                                # 8888 on very old FW
    "header":  project_root / "config" / "header.json",
    "out":     project_root / "data" / "live.dta.csv",
}

# german decimal comma like the USB export
locale.setlocale(locale.LC_NUMERIC, "de_DE.UTF-8")

header = json.loads(CFG["header"].read_text())
hp = Luxtronik(CFG["hp_ip"], CFG["hp_port"])
read_result = hp.read()
if read_result is None:
    print(f"Error: Could not connect to heat pump at {CFG['hp_ip']}:{CFG['hp_port']}")
    exit(1)
calculations, parameters, _ = read_result

now = dt.datetime.now()
row = {
    "Timestamp": int(now.timestamp()),
    "DateTime":  now.strftime("%d.%m.%Y %H:%M:%S"),
}
calc_dict = {c.name: c.value for c in calculations}
param_dict = {p.name: p.value for p in parameters}
row.update(calc_dict)
row.update(param_dict)

# keep *exact* column order & pads missing keys with empty field
row = {k: (locale.format_string("%.1f", row[k]) if isinstance(row.get(k), float) else row.get(k, ""))
        for k in header}

CFG["out"].parent.mkdir(parents=True, exist_ok=True)
write_head = not CFG["out"].exists()
with CFG["out"].open("a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=header, delimiter=";", lineterminator="\r\n")
    if write_head:
        w.writeheader()
    w.writerow(row)
