#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

# Load data
matches = pd.read_csv("matches.csv", index_col=0)

# Data preprocessing steps
def rolling_averages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed='left').mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group

cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{c}_rolling" for c in cols]

matches_rolling = matches.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
if 'team' in matches_rolling.index.names:
    matches_rolling = matches_rolling.droplevel('team')

matches_rolling.index = range(matches_rolling.shape[0])

# Define predictors
predictors = ["venue_code", "opp_code", "hour", "day_code"] + new_cols

# Train the RandomForestClassifier
rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)
train = matches[matches["date"] < '2022-01-01']
rf.fit(train[predictors], train["target"])

# Make predictions
combined, error = make_predictions(matches_rolling, predictors)

# Further analysis and output
combined = combined.merge(matches_rolling[["date", "team", "opponent", "result"]], left_index=True, right_index=True)

class MissingDict(dict):
    __missing__ = lambda self, key: key

map_values = {"Brighton and Hove Albion": "Brighton", "Manchester United": "Manchester Utd", 
              "Newcastle United": "Newcastle Utd", "Tottenham Hotspur": "Tottenham", 
              "West Ham United": "West Ham", "Wolverhampton Wanderers": "Wolves"}

mapping = MissingDict(**map_values)
combined["new_team"] = combined["team"].map(mapping)

merged = combined.merge(combined, left_on=["date", "new_team"], right_on=["date", "opponent"])

# Further analysis and output
print("Precision Score:", error)
print("Top cases where model predicted a win (1) and actual result was a loss (0):")
print(merged[(merged["predicted_x"] == 1) & (merged["predicted_y"] == 0)]["actual_x"].value_counts())
