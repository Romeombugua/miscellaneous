import pandas as pd

# Read the Excel file
df = pd.read_csv('file2_cleaned.csv')

# Print the column names to check the actual column names
print(df.columns)


# Remove duplicate rows based on the name column
df_unique = df.drop_duplicates(subset=["Name"], keep='first')

# Save the cleaned and unique DataFrame to a new Excel file
df_unique.to_csv('run3.csv', index=False)
