import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

conn = sqlite3.connect("pickleball.db")

# Get the full list of shot types that actually appear as final shots
shot_types_query = """
SELECT DISTINCT st.shot_type_desc
FROM shot s
JOIN rally r ON s.rally_id = r.rally_id
JOIN (
    SELECT rally_id, MAX(shot_nbr) AS max_shot_nbr
    FROM shot
    GROUP BY rally_id
) m ON s.rally_id = m.rally_id AND s.shot_nbr = m.max_shot_nbr
LEFT JOIN shot_type_ref st ON s.shot_type = st.shot_type
WHERE r.ending_type IN ('Winner', 'Error', 'Unforced Error')
  AND st.shot_type_desc IS NOT NULL
"""
shot_types_df = pd.read_sql_query(shot_types_query, conn)
shot_types = shot_types_df["shot_type_desc"].tolist()
print(f"Found {len(shot_types)} shot types: {shot_types}\n")

stats_query = """
SELECT 
    g.skill_lvl,
    COUNT(*) AS num_final_shots,
    SUM(CASE WHEN r.ending_type = 'Winner' THEN 1 ELSE 0 END) AS num_winners,
    ROUND(100.0 * SUM(CASE WHEN r.ending_type = 'Winner' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_winner
FROM shot s
JOIN rally r ON s.rally_id = r.rally_id
JOIN game g ON r.game_id = g.game_id
JOIN (
    SELECT rally_id, MAX(shot_nbr) AS max_shot_nbr
    FROM shot
    GROUP BY rally_id
) m ON s.rally_id = m.rally_id AND s.shot_nbr = m.max_shot_nbr
LEFT JOIN shot_type_ref st ON s.shot_type = st.shot_type
WHERE r.ending_type IN ('Winner', 'Error', 'Unforced Error')
  AND st.shot_type_desc = ?
GROUP BY g.skill_lvl
ORDER BY g.skill_lvl
"""

# Create an output folder for the reports
os.makedirs("scouting_reports", exist_ok=True)

all_reports = []

for shot_type in shot_types:
    print(f"Generating report for: {shot_type}")

    df = pd.read_sql_query(stats_query, conn, params=(shot_type,))
    stats_text = df.to_string(index=False)

    prompt = f"""You are a pickleball performance analyst reviewing shot-level data from competitive matches.

Here is the win rate breakdown for the "{shot_type}" shot type when it is the final shot of a rally, broken down by skill level:

{stats_text}

Write a concise scouting report (4-5 sentences) that:
1. States the overall pattern across skill levels
2. Notes any skill level where this shot performs notably better or worse than others
3. Explicitly flags any skill level with fewer than 30 final shots as having a small, less reliable sample size
4. Offers one strategic takeaway a player or coach could act on

Use plain language suitable for a player who is not a data analyst. Do not invent statistics beyond what is provided above."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    report_text = response.content[0].text

    # Save individual file
    safe_filename = shot_type.replace(" ", "_").replace("/", "_")
    with open(f"scouting_reports/{safe_filename}.txt", "w", encoding="utf-8") as f:
        f.write(f"=== {shot_type} ===\n\n")
        f.write(f"Raw stats:\n{stats_text}\n\n")
        f.write(f"AI-Generated Report:\n{report_text}\n")

    all_reports.append(f"=== {shot_type} ===\n{report_text}\n")
    print(f"  Done.\n")

conn.close()

# Also save one combined file with everything
with open("scouting_reports/all_reports_combined.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_reports))

print(f"\nAll {len(shot_types)} reports saved to the 'scouting_reports' folder.")