# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Export Q4 Roadmap to Excel with current status
"""

from datetime import datetime

import pandas as pd
from drucker_management import DEFAULT_ROADMAP_ITEMS


def export_roadmap_to_excel():
    """Export current Q4 roadmap to Excel with updated status"""

    # Convert roadmap items to DataFrame
    df = pd.DataFrame(DEFAULT_ROADMAP_ITEMS)

    # Add current timestamp
    df["export_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate status counts
    status_counts = df["status"].value_counts()
    completed_count = status_counts.get("Completed", 0)
    total_count = len(df)

    # Add summary sheet data
    summary_data = {
        "Metric": [
            "Total Items",
            "Completed Items",
            "Completion Rate",
            "In Progress Items",
            "Not Started Items",
            "Export Date",
        ],
        "Value": [
            total_count,
            completed_count,
            f"{completed_count}/{total_count} ({completed_count / total_count * 100:.1f}%)",
            status_counts.get("In Progress", 0),
            status_counts.get("Not Started", 0),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ],
    }
    summary_df = pd.DataFrame(summary_data)

    # Create Excel writer
    with pd.ExcelWriter("roadmap_export_updated.xlsx", engine="openpyxl") as writer:
        # Main roadmap data
        df.to_excel(writer, sheet_name="Q4_Roadmap", index=False)

        # Summary sheet
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # Status breakdown
        status_breakdown = (
            df.groupby(["phase", "status"]).size().reset_index(name="count")
        )
        status_breakdown.to_excel(writer, sheet_name="Status_Breakdown", index=False)

        # Priority analysis
        priority_analysis = (
            df.groupby(["priority", "status"]).size().reset_index(name="count")
        )
        priority_analysis.to_excel(writer, sheet_name="Priority_Analysis", index=False)

    print(f"✅ Exported {len(df)} roadmap items to roadmap_export_updated.xlsx")
    print(
        f"📊 Status: {completed_count}/{total_count} completed ({completed_count / total_count * 100:.1f}%)"
    )

    return df


if __name__ == "__main__":
    export_roadmap_to_excel()
