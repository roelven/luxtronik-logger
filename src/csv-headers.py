import csv, json, pathlib
TEMPLATE = pathlib.Path("320210-717_250713_1340.dta.csv")  # your sample
with TEMPLATE.open(newline="") as f:
    HEADER = next(csv.reader(f, delimiter=";"))            # detects 155 cols
pathlib.Path("header.json").write_text(json.dumps(HEADER))