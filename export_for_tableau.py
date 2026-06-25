import sqlite3
import pandas as pd
import os

conn = sqlite3.connect("pickleball.db")
os.makedirs("tableau_exports", exist_ok=True)

# Export 1: Rally length by skill level
print("Exporting rally length by skill level...")
query1 = """
SELECT 
    g.skill_lvl,
    r.rally_len,
    r.ending_type
FROM rally r
JOIN game g ON r.game_id = g.game_id
WHERE r.ending_type IN ('Winner', 'Error', 'Unforced Error')
"""
df1 = pd.read_sql_query(query1, conn)
df1.to_csv("tableau_exports/rally_length_by_skill.csv", index=False)
print(f"  Saved {len(df1)} rows.")

# Export 2: Ending type breakdown by skill level (counts, Tableau can calculate %)
print("Exporting ending type breakdown by skill level...")
query2 = """
SELECT 
    g.skill_lvl,
    r.ending_type,
    COUNT(*) AS num_rallies
FROM rally r
JOIN game g ON r.game_id = g.game_id
WHERE r.ending_type IN ('Winner', 'Error', 'Unforced Error')
GROUP BY g.skill_lvl, r.ending_type
"""
df2 = pd.read_sql_query(query2, conn)
df2.to_csv("tableau_exports/ending_type_by_skill.csv", index=False)
print(f"  Saved {len(df2)} rows.")

# Export 3: Shot type winner rate by skill level (the full breakdown table)
print("Exporting shot type winner rates...")
query3 = """
SELECT 
    g.skill_lvl,
    st.shot_type_desc,
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
  AND st.shot_type_desc IS NOT NULL
GROUP BY g.skill_lvl, st.shot_type_desc
"""
df3 = pd.read_sql_query(query3, conn)
df3.to_csv("tableau_exports/shot_type_winner_rate.csv", index=False)
print(f"  Saved {len(df3)} rows.")

# Export 4: All shot locations for heatmap (with skill level for filtering)
print("Exporting shot locations for heatmap...")
query4 = """
SELECT 
    s.loc_x,
    s.loc_y,
    g.skill_lvl,
    CASE WHEN r.ending_type = 'Winner' AND s.shot_nbr = (
        SELECT MAX(s2.shot_nbr) FROM shot s2 WHERE s2.rally_id = s.rally_id
    ) THEN 'Winning Shot' ELSE 'Other Shot' END AS shot_category
FROM shot s
JOIN rally r ON s.rally_id = r.rally_id
JOIN game g ON r.game_id = g.game_id
WHERE s.loc_x IS NOT NULL AND s.loc_y IS NOT NULL
"""
df4 = pd.read_sql_query(query4, conn)
df4.to_csv("tableau_exports/shot_locations.csv", index=False)
print(f"  Saved {len(df4)} rows.")

conn.close()
print("\nAll exports complete! Check the 'tableau_exports' folder.")