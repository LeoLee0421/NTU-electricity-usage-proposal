# Import packages

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from tqdm import tqdm
import os
from google.colab import drive

# Set paths of request and output

url = "https://gra206.aca.ntu.edu.tw/classrm/acarm/check-by-date1-new"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "zh-TW,zh-Hant;q=0.9"
}

drive.mount('/content/drive', force_remount=True)
OUTPUT_FOLDER = "/content/drive/MyDrive/NTU/Data Science of Env and Eng/data/putong-class-timetable"

# Set request days

start_date = datetime(2026, 2, 23)
end_date = datetime(2026, 4, 17)

dates = []
current_date = start_date
while current_date <= end_date:
    if current_date.weekday() < 5:
        dates.append(current_date)
    current_date += timedelta(days=1)
    
# Processing

for current_date in tqdm(dates, desc="Processing dates"):
    
    # Set time
    date_str = current_date.strftime("%Y-%m-%d")
    daily_dfs = []
    
    # Read in request files
    for page in [1, 2, 3]:
        params = {
            "page": page,
            "DateDDL": date_str,
            "BuildingDDL": "普通",
            "Capacity": 1,
            "SelectButton": "查詢"
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed on {date_str}, page {page}")
            continue
        
        try:
            dfs = pd.read_html(response.text)
            df = dfs[2]
            daily_dfs.append(df)
        except Exception as e:
            print(f"Error on {date_str}, page {page}: {e}")
    
    if not daily_dfs:
        continue

    # Concat three pages
    df = pd.concat(daily_dfs, ignore_index=True)

    # Preprocessing =========================================================

    # Drop last row
    df = df.drop(df.index[-1])

    # Separate room and capacity
    first_col = df.columns[0]
    df[['room', 'capacity']] = df[first_col].str.extract(r'(普\d+)\s*(\d+)人')
    df = df.dropna(subset=['room', 'capacity'])
    df['capacity'] = df['capacity'].astype(int)

    # Set room as index
    df = df.drop(columns=[first_col])
    df = df.set_index('room')

    # Set time as MultiIndex columns
    cols = df.columns
    new_cols = []

    for col in cols:
        if col == "capacity":
            new_cols.append(("capacity", "", ""))
            continue

        parts = str(col).split()
        if len(parts) == 3: start, end, period = parts
        else: start, end, period = None, None, None
        new_cols.append((start, end, period))

    df.columns = pd.MultiIndex.from_tuples(new_cols, names=["start", "end", "period"])

    # Save =================================================================

    filename = f"putong_timetable_{date_str}.csv"
    df.to_csv(os.path.join(OUTPUT_FOLDER, filename))
    time.sleep(1)