import csv, json, pathlib

# Determine the project root directory
project_root = pathlib.Path(__file__).parent.parent

TEMPLATE = project_root / "data" / "320210-717_250713_1340.dta.csv"  # your sample
with TEMPLATE.open(newline="") as f:
    HEADER = next(csv.reader(f, delimiter=";"))            # detects 155 cols
(project_root / "config" / "header.json").write_text(json.dumps(HEADER))
