import pandas as pd
import os

def process_dataframe(file_path):
    # 1. Load the excel file
    df = pd.read_excel(file_path)
    
    # 2. Remove columns that are completely empty
    df_cleaned = df.dropna(axis=1, how='all')
    
    # 3. Cleanup the dataframe
    df_cleaned["Index"] = df_cleaned["Index"].str.replace("#", "")
    df_cleaned.drop("Propose Time", axis=1, inplace=True, errors='ignore')
    df_cleaned["Status"] = df_cleaned["Status"].str.replace("Awarded\n", "")
    
    # 4. Split the "Value" column into "DOT" and "USD"
    df_cleaned["DOT"] = df_cleaned["Value"].str.split("\n").str[0]
    df_cleaned["USD"] = df_cleaned["Value"].str.split("\n").str[-1]
    df_cleaned.drop("Value", axis=1, inplace=True)
    
    # 5. Replace commas with dots and dots with commas
    df_cleaned["DOT"] = df_cleaned["DOT"].str.replace('.', '#').str.replace(',', '.').str.replace('#', ',')
    df_cleaned["USD"] = df_cleaned["USD"].str.replace('.', '#').str.replace(',', '.').str.replace('#', ',')
    
    # 6. Convert DOT and USD columns to numbers
    df_cleaned["DOT"] = df_cleaned["DOT"].str.replace(',', '').astype(float)
    df_cleaned["USD"] = df_cleaned["USD"].str.replace('≈ \$', '').str.replace(',', '').astype(float)
    
    # 7. Rename "Status" to "Awarded" and only keep the date
    df_cleaned.rename(columns={"Status": "Awarded"}, inplace=True)
    df_cleaned["Awarded"] = df_cleaned["Awarded"].str.split().str[0]
    
    # 8. Reorder the columns
    df_final = df_cleaned[["Index", "Awarded", "DOT", "USD", "Beneficiary", "Description"]]
    
    return df_final

def create_links_markdown(df, output_path, subsquare_template, polkassembly_template):
    with open(output_path, 'w') as md_file:
        for beneficiary, group in df.groupby('Beneficiary'):
            # Add new columns with links
            group["Subsquare"] = group["Index"].apply(lambda x: f"[View on Subsquare]({subsquare_template}{x})")
            group["Polkassembly"] = group["Index"].apply(lambda x: f"[View on Polkassembly]({polkassembly_template}{x})")
            
            # Sort the 'Awarded' column within each group
            sorted_group = group.sort_values(by="Awarded")
            
            # Format the DOT and USD columns
            sorted_group["DOT"] = sorted_group["DOT"].astype(int).apply("{:,}".format)
            sorted_group["USD"] = sorted_group["USD"].astype(int).apply("{:,}".format)
            
            md_file.write(f"## {beneficiary}\n\n")
            md_file.write(sorted_group.drop('Beneficiary', axis=1).to_markdown(index=False))
            md_file.write("\n\n")

# Example usage:
file_path = "/mnt/data/Untitled spreadsheet.xlsx"
processed_df = process_dataframe(file_path)

# Set the link templates
subsquare_template = "https://polkadot.subsquare.io/treasury/proposal/"
polkassembly_template = "https://polkadot.polkassembly.io/treasury/"

# Create markdown with links grouped by beneficiary
output_dir = "/mnt/data/markdown_files"
links_markdown_file_path = os.path.join(output_dir, "grouped_by_beneficiary_links.md")
create_links_markdown(processed_df, links_markdown_file_path, subsquare_template, polkassembly_template)

print("Markdown file with links created:", links_markdown_file_path)
