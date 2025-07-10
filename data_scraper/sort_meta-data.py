import pandas as pd

df = pd.read_csv("data/meta-data.csv")

# Drop columns by index
cols_to_drop = [0, 8, 15, 18, 19, 20, 21, 22]  # columns at index 0 and 2

# Get column names by index
col_names_to_drop = df.columns[cols_to_drop]

# Drop columns by name
df = df.drop(columns=col_names_to_drop)

# Save result
df.to_csv("data/out/houses-meta-data.csv", index=False)
