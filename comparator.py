import pandas as pd

# Read the Excel files
file1 = pd.read_csv('oldsocial.csv')
file2 = pd.read_csv('newsocial.csv')

# Print the column names to check the actual column names
print(file1.columns)
print(file2.columns)

# Assuming the column containing the names is 'Name' in both files
name_column_name = 'Website'  # Replace 'Name' with the actual column name if it's different

# Get the set of names from file1
names_to_remove = set(file1[name_column_name])

# Filter out rows in file2 where the Name is in file1
file2_cleaned = file2[~file2[name_column_name].isin(names_to_remove)]

# Save the cleaned file2 to a new Excel file
file2_cleaned.to_csv('newsc_cleaned.csv', index=False)
