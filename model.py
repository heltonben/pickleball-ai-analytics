import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

print("Starting script...")

conn = sqlite3.connect("pickleball.db")
print("Connected to database.")

# Pull the final shot of each rally, joined with rally outcome, skill level, and shot type
query = """
SELECT 
    r.rally_id,
    r.rally_len,
    r.ending_type,
    g.skill_lvl,
    s.loc_x,
    s.loc_y,
    st.shot_type_desc,
    CASE WHEN s.player_id = r.srv_player_id THEN 1 ELSE 0 END AS is_server
FROM rally r
JOIN game g ON r.game_id = g.game_id
JOIN shot s ON s.rally_id = r.rally_id
JOIN (
    SELECT rally_id, MAX(shot_nbr) AS max_shot_nbr
    FROM shot
    GROUP BY rally_id
) m ON s.rally_id = m.rally_id AND s.shot_nbr = m.max_shot_nbr
LEFT JOIN shot_type_ref st ON s.shot_type = st.shot_type
WHERE r.ending_type IN ('Winner', 'Error', 'Unforced Error')
"""

df = pd.read_sql_query(query, conn)
conn.close()
print(f"Loaded {len(df)} rows.")

print(df.head())
print(df["ending_type"].value_counts())

print("\nPreparing data for modeling...")

# Combine Error and Unforced Error into one "Loss" category
df["outcome"] = df["ending_type"].apply(lambda x: 1 if x == "Winner" else 0)

# Convert numeric columns from text to actual numbers
df["rally_len"] = pd.to_numeric(df["rally_len"])
df["loc_x"] = pd.to_numeric(df["loc_x"])
df["loc_y"] = pd.to_numeric(df["loc_y"])

# Drop rows with missing values in our key columns
df = df.dropna(subset=["rally_len", "loc_x", "loc_y", "skill_lvl", "shot_type_desc"])

# One-hot encode categorical variables
df_encoded = pd.get_dummies(df, columns=["skill_lvl", "shot_type_desc"], drop_first=True)

# Define features (X) and target (y)
feature_cols = [col for col in df_encoded.columns if col not in 
                ["rally_id", "ending_type", "outcome"]]
X = df_encoded[feature_cols]
y = df_encoded["outcome"]

print(f"Final dataset: {len(X)} rows, {len(feature_cols)} features")
print(f"Outcome balance:\n{y.value_counts()}")

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining set: {len(X_train)} rows")
print(f"Test set: {len(X_test)} rows")

# Fit the logistic regression model, accounting for class imbalance
model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.3f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nFeature coefficients (sorted by impact):")
coef_df = pd.DataFrame({
    "feature": X.columns,
    "coefficient": model.coef_[0]
})
coef_df["abs_coefficient"] = coef_df["coefficient"].abs()
coef_df = coef_df.sort_values("abs_coefficient", ascending=False)

print(coef_df[["feature", "coefficient"]].to_string(index=False))

