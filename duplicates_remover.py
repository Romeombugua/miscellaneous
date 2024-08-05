import csv
from urllib.parse import urlparse
import os

# Function to extract the account name from the URL
def extract_account_name(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    if 'facebook.com' in parsed_url.netloc or 'instagram.com' in parsed_url.netloc:
        if len(path_parts) > 1:
            return path_parts[1]
    return None

# Read the original CSV file and filter out duplicate accounts
def remove_duplicate_accounts(input_csv, output_csv):
    try:
        seen_accounts = set()
        cleaned_rows = []

        with open(input_csv, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # Read the header
            cleaned_rows.append(header)

            for row in csv_reader:
                url = row[4]  # Assuming the URL is in the 5th column
                account_name = extract_account_name(url)

                if account_name and account_name not in seen_accounts:
                    seen_accounts.add(account_name)
                    cleaned_rows.append(row)

        # Write the cleaned data to a new CSV file
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(cleaned_rows)

        print(f"Duplicates removed. Cleaned data saved to {output_csv}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# File paths
input_csv = 'keyword.csv'
output_csv = 'keyword_clean.csv'

# Remove duplicates
remove_duplicate_accounts(input_csv, output_csv)
