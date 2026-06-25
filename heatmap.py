import matplotlib
matplotlib.use("Agg")

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

print("Starting script...")

conn = sqlite3.connect("pickleball.db")
print("Connected to database.")

all_shots_query = """
SELECT loc_x, loc_y
FROM shot
WHERE loc_x IS NOT NULL AND loc_y IS NOT NULL
"""
all_shots = pd.read_sql_query(all_shots_query, conn)
print(f"Query 1 done, {len(all_shots)} rows.")

winner_shots_query = """
SELECT s.loc_x, s.loc_y
FROM shot s
JOIN rally r ON s.rally_id = r.rally_id
JOIN (
    SELECT rally_id, MAX(shot_nbr) AS max_shot_nbr
    FROM shot
    GROUP BY rally_id
) m ON s.rally_id = m.rally_id AND s.shot_nbr = m.max_shot_nbr
WHERE r.ending_type = 'Winner'
  AND s.loc_x IS NOT NULL AND s.loc_y IS NOT NULL
"""
winner_shots = pd.read_sql_query(winner_shots_query, conn)
print(f"Query 2 done, {len(winner_shots)} rows.")

conn.close()
print("Database closed. Starting plots...")

all_shots["loc_x"] = pd.to_numeric(all_shots["loc_x"])
all_shots["loc_y"] = pd.to_numeric(all_shots["loc_y"])
winner_shots["loc_x"] = pd.to_numeric(winner_shots["loc_x"])
winner_shots["loc_y"] = pd.to_numeric(winner_shots["loc_y"])

# Court boundary reference lines (in feet, based on official dimensions)
SIDELINE_LEFT = 0
SIDELINE_RIGHT = 20
CENTERLINE = 10

def add_court_lines(ax):
    ax.axvline(SIDELINE_LEFT, color="cyan", linestyle="--", linewidth=1, label="Sideline")
    ax.axvline(SIDELINE_RIGHT, color="cyan", linestyle="--", linewidth=1)
    ax.axvline(CENTERLINE, color="lime", linestyle=":", linewidth=1, label="Centerline")
    ax.set_xlim(-5, 25)
    ax.set_ylim(0, 25)

print("Plotting all shots...")
fig, ax = plt.subplots(figsize=(8, 10))
hb = ax.hexbin(all_shots["loc_x"], all_shots["loc_y"], gridsize=40, cmap="hot")
plt.colorbar(hb, label="Shot density")
add_court_lines(ax)
ax.legend(loc="upper right", fontsize=8)
ax.set_title("Heatmap of All Shot Locations (Hitting Player's Perspective)")
ax.set_xlabel("Distance from sideline (feet)")
ax.set_ylabel("Distance from net (feet)")
plt.savefig("all_shots_heatmap.png")
print("Saved all_shots_heatmap.png")

print("Plotting winner shots...")
fig, ax = plt.subplots(figsize=(8, 10))
hb = ax.hexbin(winner_shots["loc_x"], winner_shots["loc_y"], gridsize=40, cmap="hot")
plt.colorbar(hb, label="Shot density")
add_court_lines(ax)
ax.legend(loc="upper right", fontsize=8)
ax.set_title("Heatmap of Winning Shot Locations (Hitting Player's Perspective)")
ax.set_xlabel("Distance from sideline (feet)")
ax.set_ylabel("Distance from net (feet)")
plt.savefig("winner_shots_heatmap.png")
print("Saved winner_shots_heatmap.png")

print("Done! Check your project folder for the two PNG files.")