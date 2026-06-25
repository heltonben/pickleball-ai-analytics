-- Skill level distribution
SELECT skill_lvl, COUNT(*) AS num_games
FROM game
GROUP BY skill_lvl
ORDER BY num_games DESC;

-- Ending type distribution
SELECT ending_type, COUNT(*) AS num_rallies
FROM rally
GROUP BY ending_type
ORDER BY num_rallies DESC;

-- Average rally length by skill level
SELECT g.skill_lvl, AVG(r.rally_len) AS avg_rally_length, COUNT(*) AS num_rallies
FROM rally r
JOIN game g ON r.game_id = g.game_id
GROUP BY g.skill_lvl
ORDER BY avg_rally_length DESC;

-- Shot type distribution
SELECT shot_type, COUNT(*) AS num_shots
FROM shot
GROUP BY shot_type
ORDER BY num_shots DESC;

--Ending type by skill level
SELECT 
    g.skill_lvl,
    r.ending_type,
    COUNT(*) AS num_rallies,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY g.skill_lvl), 1) AS pct_of_skill_level
FROM rally r
JOIN game g ON r.game_id = g.game_id
WHERE r.ending_type IS NOT NULL
GROUP BY g.skill_lvl, r.ending_type
ORDER BY g.skill_lvl, pct_of_skill_level DESC;

-- Shot distribution for heatmap
SELECT 
    CASE 
        WHEN CAST(loc_x AS REAL) < -20 THEN 'below -20'
        WHEN CAST(loc_x AS REAL) >= -20 AND CAST(loc_x AS REAL) < -10 THEN '-20 to -10'
        WHEN CAST(loc_x AS REAL) >= -10 AND CAST(loc_x AS REAL) < 0 THEN '-10 to 0'
        WHEN CAST(loc_x AS REAL) >= 0 AND CAST(loc_x AS REAL) < 10 THEN '0 to 10'
        WHEN CAST(loc_x AS REAL) >= 10 AND CAST(loc_x AS REAL) < 20 THEN '10 to 20'
        WHEN CAST(loc_x AS REAL) >= 20 THEN '20 and above'
    END AS x_bucket,
    COUNT(*) AS num_shots
FROM shot
WHERE loc_x IS NOT NULL
GROUP BY x_bucket
ORDER BY MIN(CAST(loc_x AS REAL));

SELECT 
    shot_nbr,
    COUNT(*) AS num_shots
FROM shot
WHERE loc_y IS NOT NULL
  AND CAST(loc_y AS REAL) >= 1 AND CAST(loc_y AS REAL) < 2
GROUP BY shot_nbr
ORDER BY num_shots DESC
LIMIT 10;


--Winning shot distribution for heatmap
SELECT 
    CASE WHEN s.player_id = r.srv_player_id THEN 'Server' ELSE 'Non-server' END AS player_role,
    ROUND(AVG(CAST(s.loc_y AS REAL)), 1) AS avg_loc_y,
    COUNT(*) AS num_shots
FROM shot s
JOIN rally r ON s.rally_id = r.rally_id
WHERE s.loc_y IS NOT NULL
GROUP BY player_role;

SELECT 
    CASE WHEN s.player_id IN (
        SELECT player_id FROM team WHERE team_id = r.w_team_id
    ) THEN 'Winning team shot' ELSE 'Losing team shot' END AS team_outcome,
    ROUND(AVG(CAST(s.loc_y AS REAL)), 1) AS avg_loc_y,
    COUNT(*) AS num_shots
FROM shot s
JOIN rally r ON s.rally_id = r.rally_id
WHERE s.loc_y IS NOT NULL
GROUP BY team_outcome;