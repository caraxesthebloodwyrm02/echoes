"""
Data Analysis: Category & Section Analysis
Analyzes distribution, breakdown, and hierarchical structure
"""

import pandas as pd
from pathlib import Path
import sys


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"{title:^70}")
    print("=" * 70)


def load_data():
    """Load and return the data with error handling."""
    try:
        csv_path = Path(__file__).parent / "DESIGN_PHILOSOPHY.csv"
        print(f"\nLoading data from: {csv_path}")

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")

        df = pd.read_csv(csv_path)
        print(f"Successfully loaded {len(df)} rows")
        return df

    except Exception as e:
        print(f"\n❌ Error loading data: {str(e)}")
        print("Please ensure the CSV file exists and is properly formatted.")
        sys.exit(1)


# Initialize data
category_distribution = {"Category A": "35%", "Category B": "20%", "Category C": "25%", "Category D": "20%"}

section_breakdown = {
    "Category A": {"Section 1": {"LightBlue": 30, "Medium": 25, "DarkBlue": 45}},
    "Category B": {"Section 2": {"LightBlue": 20, "Medium": 35, "DarkBlue": 45}},
    "Category C": {"Section 3": {"LightBlue": 15, "Medium": 40, "DarkBlue": 45}},
}

tree_structure = {"Root": ["A", "B"]}


def analyze_category_distribution(df):
    """Analyze and display category distribution."""
    print_header("CATEGORY DISTRIBUTION")

    # Display the predefined category distribution
    print("\n📊 PRE-DEFINED CATEGORY DISTRIBUTION:")
    print("-" * 70)
    for category, percentage in category_distribution.items():
        bar = "█" * int(float(percentage.strip("%")) / 2)
        print(f"{category:20} {percentage:>5} {bar}")

    # If we have CSV data, show that too
    if not df.empty and "Category" in df.columns:
        category_counts = df["Category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]
        category_counts = category_counts.sort_values("Count", ascending=False)

        print("\n📊 CSV-BASED CATEGORY DISTRIBUTION:")
        print("-" * 70)
        for idx, row in category_counts.iterrows():
            bar = "█" * int(row["Count"] / 2)
            percentage = (row["Count"] / len(df)) * 100
            print(f"{row['Category']:35s} {bar} {row['Count']:3d} ({percentage:5.1f}%)")

        print(f"\nTotal Categories: {len(category_counts)}")
        print(f"Most Common: {category_counts.iloc[0]['Category']} ({category_counts.iloc[0]['Count']} entries)")


def analyze_section_breakdown(df):
    """Analyze and display section breakdown."""
    print_header("SECTION BREAKDOWN")

    # Display the predefined section breakdown
    print("\n📊 PRE-DEFINED SECTION BREAKDOWN:")
    print("-" * 70)
    for category, sections in section_breakdown.items():
        print(f"\n{category}:")
        for section, values in sections.items():
            print(f"  {section}:")
            for k, v in values.items():
                print(f"    {k}: {v}")

    # If we have CSV data, show that too
    if not df.empty and "Section" in df.columns:
        section_counts = df["Section"].value_counts().reset_index()
        section_counts.columns = ["Section", "Count"]
        section_counts = section_counts.sort_values("Section")

        print("\n📊 CSV-BASED SECTION DISTRIBUTION:")
        print("-" * 70)
        for idx, row in section_counts.iterrows():
            bar = "▓" * int(row["Count"] / 2)
            percentage = (row["Count"] / len(df)) * 100
            print(f"{row['Section']:45s} {bar} {row['Count']:3d} ({percentage:5.1f}%)")

        print(f"\nTotal Sections: {len(section_counts)}")
        print(
            f"Largest Section: {section_counts.loc[section_counts['Count'].idxmax(), 'Section']} "
            f"({section_counts['Count'].max()} entries)"
        )


def main():
    """Main function to run the analysis."""
    print_header("GLIMPSE DATA ANALYSIS")

    # Load the data
    df = load_data()

    # Run analyses
    analyze_category_distribution(df)


if __name__ == "__main__":
    main()
print(f"Unique Sections:            {df['Section'].nunique()}")
print(f"Unique Subsections:         {df['Subsection'].nunique()}")
print(f"Unique Categories:          {df['Category'].nunique()}")
print(f"Unique Key Concepts:        {df['Key Concept'].nunique()}")
print(f"Entries with Descriptions:  {df['Description'].notna().sum()}")
print(f"Entries with Details:       {df['Details'].notna().sum()}")
print(f"Entries with Status:        {df['Status'].notna().sum()}")

# Average entries per section
avg_per_section = len(df) / df["Section"].nunique()
print(f"Average entries per section: {avg_per_section:.1f}")

# Average entries per category
avg_per_category = len(df) / df["Category"].nunique()
print(f"Average entries per category: {avg_per_category:.1f}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
