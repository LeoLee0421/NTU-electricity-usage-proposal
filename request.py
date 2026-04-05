import requests
import pandas as pd

url = "https://gra206.aca.ntu.edu.tw/classrm/acarm/check-by-date1-new"

params = {
    "page": 1,
    "DateDDL": "2026-04-01",
    "BuildingDDL": "普通",
    "Capacity": 1,
    "SelectButton": "查詢"
}

headers = {
    "User-Agent": "Your user-agent",
    "Accept-Language": "zh-TW,zh-Hant;q=0.9"
}

response = requests.get(url, params=params, headers=headers)


print("Status code:", response.status_code)
dfs = pd.read_html(response.text)

df = dfs[2]
df

# Drop last row
df = df.drop(df.index[-1])

# Seperate room and capacity
first_col = df.columns[0]
df[['room', 'capacity']] = df[first_col].str.extract(r'(普\d+)\s*(\d+)人')
df['capacity'] = df['capacity'].astype(int)

# Set room as index
df = df.drop(columns=[first_col])
df = df.set_index('room')

df

cols = df.columns
new_cols = []

for col in cols:
    if col == "capacity":
        new_cols.append(("capacity", "", ""))
        continue

    parts = str(col).split()

    if len(parts) == 3:
        start, end, period = parts
    else:
        start, end, period = None, None, None

    new_cols.append((start, end, period))

df.columns = pd.MultiIndex.from_tuples(
    new_cols,
    names=["start", "end", "period"]
)

df

# Create binary table of class or no class
capacity_col = df['capacity']
df_courses = df.drop(columns=['capacity'])
df_binary = df_courses.notna().astype(int)
df_binary['capacity'] = capacity_col

df_binary
