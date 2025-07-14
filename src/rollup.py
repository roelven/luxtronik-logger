import pandas as pd
import datetime as dt
import pathlib

# Determine the project root directory
project_root = pathlib.Path(__file__).parent.parent
data_dir = project_root / "data"

today = dt.date.today()
yesterday = today - dt.timedelta(days=1)

live_file = data_dir / "live.dta.csv"
rollup_file = data_dir / f"{yesterday.isoformat()}.csv"

if live_file.exists():
    df = pd.read_csv(live_file, delimiter=";")
    df["DateTime"] = pd.to_datetime(df["DateTime"], format="%d.%m.%Y %H:%M:%S")
    
    yesterday_df = df[df["DateTime"].dt.date == yesterday]
    
    if not yesterday_df.empty:
        yesterday_df.to_csv(rollup_file, index=False, sep=";")
        
        # Remove the rolled-up data from the live file
        remaining_df = df[df["DateTime"].dt.date != yesterday]
        remaining_df.to_csv(live_file, index=False, sep=";")
