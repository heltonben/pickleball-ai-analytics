import sys
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

conn = sqlite3.connect("pickleball.db")

# Get shot type from command line, default to "Reset" if none given
if len(sys.argv) > 1:
    shot_type = sys.argv[1]
else:
    shot_type = "Reset"

print(f"Generating scouting report for shot type: {shot_type}\n")

query = """
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

df = pd.read_sql_query(query, conn, params=(shot_type,))
conn.close()

print(df)

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

print("\nSending prompt to Claude...\n")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=500,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print("=== SCOUTING REPORT ===")
print(response.content[0].text)