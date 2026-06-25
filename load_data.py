import pandas as pd
import sqlite3
import os

# Folder where your CSVs live
data_folder = "pickleballdata"

# Name of the database file that will be created
db_name = "pickleball.db"

# Connect to (or create) the SQLite database
conn = sqlite3.connect(db_name)

# List of your CSV files and the table names you want them to become
csv_files = {
    "ball_type_ref.csv": "ball_type_ref",
    "game.csv": "game",
    "player.csv": "player",
    "rally.csv": "rally",
    "shot.csv": "shot",
    "shot_type_ref.csv": "shot_type_ref",
    "team.csv": "team"
}

for file_name, table_name in csv_files.items():
    file_path = os.path.join(data_folder, file_name)
    print(f"Loading {file_name} into table '{table_name}'...")

    df = pd.read_csv(file_path, dtype=str)
    df.to_sql(table_name, conn, if_exists="replace", index=False)

    print(f"  -> {len(df)} rows loaded.")

conn.close()
print("\nAll tables loaded into pickleball.db")