from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from drucker_management import DEFAULT_ROADMAP_ITEMS, DruckerFoundationModel

# Import privacy filter for PII protection
try:
    from privacy_filter import PrivacyFilter

    privacy_filter = PrivacyFilter()
    PRIVACY_ENABLED = True
except ImportError:
    PRIVACY_ENABLED = False
    print("Warning: Privacy filter not available. Install privacy_filters.py first.")


management_model = DruckerFoundationModel(DEFAULT_ROADMAP_ITEMS)

ROADMAP_COLUMNS: List[Dict[str, Any]] = [
    {"name": "ID", "id": "id", "type": "numeric", "editable": False},
    {"name": "Title", "id": "title", "presentation": "input"},
    {"name": "Phase", "id": "phase", "presentation": "input"},
    {"name": "Status", "id": "status", "presentation": "input"},
    {"name": "Priority", "id": "priority", "presentation": "input"},
    {"name": "Owner", "id": "owner", "presentation": "input"},
    {"name": "Start Date", "id": "start_date", "presentation": "input"},
    {"name": "Due Date", "id": "due_date", "presentation": "input"},
    {"name": "Progress (%)", "id": "progress", "type": "numeric"},
    {"name": "Objective", "id": "objective", "presentation": "input"},
    {"name": "Notes", "id": "notes", "presentation": "input"},
]


def _status_options(records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    statuses = sorted({record.get("status", "Not Started") for record in records})
    return [{"label": status, "value": status} for status in statuses]


def _create_default_item(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a default roadmap item."""

    next_id = max((record.get("id", 0) for record in records), default=0) + 1
    today = date.today()
    future_date = today + timedelta(days=30)

    return {
        "id": next_id,
        "title": "New Item",
        "phase": "Discovery",
        "status": "Not Started",
        "priority": "Medium",
        "owner": "Unassigned",
        "start_date": today.isoformat(),
        "due_date": future_date.isoformat(),
        "progress": 0,
        "objective": "",
        "notes": "",
    }


def apply_privacy_filter(text: str) -> str:
    """Apply privacy filtering to text data"""
    if not PRIVACY_ENABLED or not text:
        return text
    return privacy_filter.mask(text)  # Use mask for dashboard display


def scan_codebase_for_pii():
    """Scan the codebase for potential PII exposure"""
    if not PRIVACY_ENABLED:
        return {"error": "Privacy filter not available"}

    try:
        from privacy_scanner import PrivacyScanner

        scanner = PrivacyScanner()

        # Scan the main Q4 directory
        from pathlib import Path

        q4_path = Path(__file__).parent
        results = scanner.scan_directory(q4_path)

        return {
            "scan_timestamp": str(pd.Timestamp.now()),
            "files_scanned": len(results),
            "pii_findings": results,
            "total_pii_found": sum(r.get("pii_found", 0) for r in results),
        }
    except ImportError:
        return {"error": "Privacy scanner not available"}


def apply_privacy_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply privacy filtering to DataFrame columns that may contain PII"""
    if not PRIVACY_ENABLED:
        return df

    # Columns that might contain PII
    pii_columns = ["owner", "objective", "notes"]

    for col in pii_columns:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).apply(apply_privacy_filter)

    return df


# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)


# App layout
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Interactive Roadmap Dashboard",
                            className="text-center my-4",
                        ),
                        html.Hr(),
                    ]
                )
            ]
        ),
        # Stats Cards
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Total Items", className="card-title"),
                                        html.H2(
                                            "0",
                                            id="total-items",
                                            className="card-text text-center",
                                        ),
                                    ]
                                )
                            ],
                            className="mb-4",
                        )
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("In Progress", className="card-title"),
                                        html.H2(
                                            "0",
                                            id="in-progress",
                                            className="card-text text-center text-warning",
                                        ),
                                    ]
                                )
                            ],
                            className="mb-4",
                        )
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Completed", className="card-title"),
                                        html.H2(
                                            "0",
                                            id="completed",
                                            className="card-text text-center text-success",
                                        ),
                                    ]
                                )
                            ],
                            className="mb-4",
                        )
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("On Hold", className="card-title"),
                                        html.H2(
                                            "0",
                                            id="on-hold",
                                            className="card-text text-center text-danger",
                                        ),
                                    ]
                                )
                            ],
                            className="mb-4",
                        )
                    ],
                    md=3,
                ),
            ]
        ),
        # Filters and Controls
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Input(
                            id="search-input",
                            type="text",
                            placeholder="Search items...",
                            className="form-control mb-3",
                        )
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="status-filter",
                            options=[],
                            multi=True,
                            placeholder="Filter by status...",
                            className="mb-3",
                        )
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Export to CSV",
                            id="export-btn",
                            color="primary",
                            className="w-100",
                        )
                    ],
                    md=2,
                ),
                dbc.Col([], md=2),
                dbc.Col(
                    [
                        dbc.Button(
                            "Privacy Scan",
                            id="privacy-scan-btn",
                            color="warning",
                            className="w-100",
                        )
                    ],
                    md=2,
                ),
            ],
            className="mb-4",
        ),
        # Auto-refresh interval (30s)
        dcc.Interval(id="refresh-interval", interval=30_000, n_intervals=0),
        # Main content area with tabs
        dbc.Tabs(
            [
                # Table View Tab
                dbc.Tab(
                    [
                        dash_table.DataTable(
                            id="roadmap-table",
                            columns=ROADMAP_COLUMNS,
                            data=management_model.to_records(),
                            page_size=15,
                            style_table={"overflowX": "auto"},
                            style_cell={
                                "textAlign": "left",
                                "padding": "10px",
                                "whiteSpace": "normal",
                                "height": "auto",
                            },
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "fontWeight": "bold",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "rgb(248, 248, 248)",
                                }
                            ],
                            editable=True,
                            row_deletable=True,
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            column_selectable="multi",
                            selected_columns=[],
                            selected_rows=[],
                            page_action="native",
                            style_data={
                                "whiteSpace": "normal",
                                "height": "auto",
                            },
                        )
                    ],
                    label="Table View",
                ),
                # Charts Tab
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col([dcc.Graph(id="status-distribution-chart")], md=6),
                                dbc.Col([dcc.Graph(id="phase-distribution-chart")], md=6),
                            ]
                        ),
                        dbc.Row([dbc.Col([dcc.Graph(id="timeline-chart")])]),
                        dbc.Row([dbc.Col([dcc.Graph(id="progress-chart")], md=12)]),
                    ],
                    label="Analytics",
                ),
            ]
        ),
        # Last updated info
        dbc.Row([dbc.Col([html.Div(id="last-updated", className="text-muted small mb-3")])]),
        # Hidden div for storing data
        dcc.Store(id="roadmap-data-store", data=management_model.to_records()),
        dcc.Download(id="download-dataframe-csv"),
        # Privacy scan modal
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Privacy Scan Results")),
                dbc.ModalBody(
                    [
                        html.Div(
                            id="privacy-scan-results",
                            children="Click 'Privacy Scan' to check for PII exposure.",
                        )
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-privacy-modal",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="privacy-modal",
            size="lg",
            is_open=False,
        ),
    ],
    fluid=True,
)


@callback(
    Output("status-filter", "options"),
    Input("roadmap-data-store", "data"),
)
def update_status_options(data: Optional[List[Dict[str, Any]]]):
    if not data:
        return []
    return _status_options(data)


@callback(
    Output("roadmap-table", "data"),
    Output("status-distribution-chart", "figure"),
    Output("phase-distribution-chart", "figure"),
    Output("timeline-chart", "figure"),
    Output("progress-chart", "figure"),
    Output("total-items", "children"),
    Output("in-progress", "children"),
    Output("completed", "children"),
    Output("on-hold", "children"),
    Output("last-updated", "children"),
    Input("roadmap-data-store", "data"),
    Input("search-input", "value"),
    Input("status-filter", "value"),
    Input("refresh-interval", "n_intervals"),
)
def refresh_dashboard(
    data: Optional[List[Dict[str, Any]]],
    search: Optional[str],
    status_filter: Optional[List[str]],
    _n: Optional[int],
):
    if not data:
        empty_fig = px.scatter(title="No data available")
        ts = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            [],
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            0,
            0,
            0,
            0,
            f"Last updated: {ts}",
        )

    df = pd.DataFrame(data)

    filtered_df = df.copy()
    if search:
        lowered = search.lower()
        search_fields = ["title", "owner", "phase", "objective", "notes"]
        search_mask = pd.Series(False, index=filtered_df.index)
        for field in search_fields:
            if field in filtered_df.columns:
                search_mask = search_mask | filtered_df[field].fillna("").str.lower().str.contains(lowered)
        filtered_df = filtered_df[search_mask]

    if status_filter:
        filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]

    # Apply privacy filtering to sensitive data
    filtered_df = apply_privacy_to_dataframe(filtered_df)

    metrics_df = filtered_df
    total = int(metrics_df.shape[0])
    in_progress = int(metrics_df[metrics_df["status"] == "In Progress"].shape[0])
    completed = int(metrics_df[metrics_df["status"] == "Completed"].shape[0])
    on_hold = int(metrics_df[metrics_df["status"] == "On Hold"].shape[0])

    if filtered_df.empty:
        empty_fig = px.scatter(title="No records match current filters")
        ts = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            [],
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            total,
            in_progress,
            completed,
            on_hold,
            f"Last updated: {ts}",
        )

    status_fig = px.pie(
        filtered_df,
        names="status",
        title="Status Distribution",
        hole=0.35,
    )

    phase_counts = filtered_df.groupby("phase").size().reset_index(name="count")
    phase_fig = px.bar(
        phase_counts,
        x="phase",
        y="count",
        color="phase",
        title="Phase Distribution",
    )

    timeline_df = filtered_df.assign(
        start_date=pd.to_datetime(filtered_df["start_date"], errors="coerce"),
        due_date=pd.to_datetime(filtered_df["due_date"], errors="coerce"),
    )
    timeline_df = timeline_df.dropna(subset=["start_date", "due_date"])
    if timeline_df.empty:
        timeline_fig = px.scatter(title="Project Timeline")
    else:
        timeline_fig = px.timeline(
            timeline_df,
            x_start="start_date",
            x_end="due_date",
            y="title",
            color="status",
            title="Project Timeline",
        )
        timeline_fig.update_yaxes(autorange="reversed")

    progress_fig = px.bar(
        filtered_df.sort_values("progress"),
        x="title",
        y="progress",
        color="phase",
        title="Progress by Initiative",
    )
    progress_fig.update_yaxes(range=[0, 100])

    filtered_records = filtered_df.sort_values("due_date").to_dict("records")

    ts = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        filtered_records,
        status_fig,
        phase_fig,
        timeline_fig,
        progress_fig,
        total,
        in_progress,
        completed,
        on_hold,
        f"Last updated: {ts}",
    )


@callback(
    Output("roadmap-data-store", "data", allow_duplicate=True),
    Input("add-item-btn", "n_clicks"),
    State("roadmap-data-store", "data"),
    prevent_initial_call=True,
)
def add_new_item(n_clicks: Optional[int], records: Optional[List[Dict[str, Any]]]):
    if not n_clicks:
        raise PreventUpdate
    records = records or []
    new_item = _create_default_item(records)
    return records + [new_item]


@callback(
    Output("roadmap-data-store", "data", allow_duplicate=True),
    Input("roadmap-table", "data_timestamp"),
    State("roadmap-table", "data"),
    State("roadmap-data-store", "data"),
    State("search-input", "value"),
    State("status-filter", "value"),
    prevent_initial_call=True,
)
def persist_table_changes(
    _,
    table_data: Optional[List[Dict[str, Any]]],
    store_data: Optional[List[Dict[str, Any]]],
    search: Optional[str],
    status_filter: Optional[List[str]],
):
    if not table_data or store_data is None:
        raise PreventUpdate

    updated_rows = {row["id"]: row for row in table_data if "id" in row}

    merged: List[Dict[str, Any]] = []
    for row in store_data:
        row_id = row.get("id")
        if row_id in updated_rows:
            merged.append({**row, **updated_rows[row_id]})
        else:
            merged.append(row)

    # Only support deletions when no external filters are active to avoid
    # incorrectly dropping records that are merely hidden.
    if not search and not status_filter:
        remaining_ids = {row.get("id") for row in table_data if "id" in row}
        merged = [row for row in merged if row.get("id") in remaining_ids]

    return merged


@callback(
    Output("download-dataframe-csv", "data"),
    Input("export-btn", "n_clicks"),
    State("roadmap-data-store", "data"),
    State("search-input", "value"),
    State("status-filter", "value"),
    prevent_initial_call=True,
)
def export_to_csv(
    n_clicks: Optional[int],
    data: Optional[List[Dict[str, Any]]],
    search: Optional[str],
    status_filter: Optional[List[str]],
):
    if not n_clicks or not data:
        raise PreventUpdate

    df = pd.DataFrame(data)

    if search:
        lowered = search.lower()
        fields = ["title", "owner", "phase", "objective", "notes"]
        mask = pd.Series(False, index=df.index)
        for field in fields:
            if field in df.columns:
                mask = mask | df[field].fillna("").str.lower().str.contains(lowered)
        df = df[mask]

    if status_filter:
        df = df[df["status"].isin(status_filter)]

    return dcc.send_data_frame(df.to_csv, "roadmap_export.csv", index=False)


@callback(
    Output("privacy-modal", "is_open"),
    Output("privacy-scan-results", "children"),
    Input("privacy-scan-btn", "n_clicks"),
    Input("close-privacy-modal", "n_clicks"),
    State("privacy-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_privacy_modal(privacy_clicks, close_clicks, is_open):
    """Handle privacy scan modal"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "privacy-scan-btn":
        # Run privacy scan
        scan_results = scan_codebase_for_pii()

        if "error" in scan_results:
            results_display = html.Div(
                [
                    html.H5("Privacy Scan Error", className="text-danger"),
                    html.P(scan_results["error"]),
                ]
            )
        else:
            # Format scan results for display
            results_display = html.Div(
                [
                    html.H5(f"Privacy Scan Results - {scan_results.get('total_pii_found', 0)} PII findings"),
                    html.P(
                        f"Scanned {scan_results.get('files_scanned', 0)} files at {scan_results.get('scan_timestamp', 'Unknown time')}"
                    ),
                    # Show findings if any
                    html.Div(
                        [
                            html.H6(
                                f"File: {finding.get('file', 'Unknown')}",
                                className="mt-3",
                            )
                            for finding in scan_results.get("pii_findings", [])
                            if finding.get("pii_found", 0) > 0
                        ],
                        className="mt-3",
                    ),
                ]
            )

        return True, results_display

    elif trigger_id == "close-privacy-modal":
        return False, dash.no_update

    return is_open, dash.no_update


# Run the app
if __name__ == "__main__":
    print("🚀 Starting Q4 Dashboard with Privacy Protection")
    print(f"📋 Privacy filtering: {'✅ Enabled' if PRIVACY_ENABLED else '❌ Disabled'}")
    if PRIVACY_ENABLED:
        print("🔒 PII protection active - sensitive data will be masked in display")
        print("🔍 Privacy scan available via 'Privacy Scan' button")
    app.run_server(debug=True, port=8050)
