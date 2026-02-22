import pandas as pd
import numpy as np
import calendar
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------
# Load and preprocess data
# -----------------------------
df = pd.read_csv("temperature_daily.csv", parse_dates=["date"])

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day

# Keep last 10 years
last_year = df["year"].max()
df = df[df["year"] >= last_year - 9]

years = sorted(df["year"].unique())
months = list(range(1, 13))

# -----------------------------
# Monthly max/min tables
# -----------------------------
monthly_max = (
    df.groupby(["year", "month"])["max_temperature"]
    .max()
    .unstack()
)

monthly_min = (
    df.groupby(["year", "month"])["min_temperature"]
    .min()
    .unstack()
)

# Global color scale limits
GLOBAL_MIN = df["min_temperature"].min()
GLOBAL_MAX = df["max_temperature"].max()

# -----------------------------
# Create matrix figure
# -----------------------------
def create_matrix(temp_type="max"):

    data = monthly_max if temp_type == "max" else monthly_min

    fig = make_subplots(
        rows=12,
        cols=len(years),
        horizontal_spacing=0.002,
        vertical_spacing=0.025,
        row_titles=[calendar.month_name[m] for m in months],
        column_titles=[str(y) for y in years],
    )

    for r, month in enumerate(months):
        for c, year in enumerate(years):

            monthly_value = data.loc[year, month]

            daily = df[(df.year == year) & (df.month == month)]

            y_values = (
                daily["max_temperature"]
                if temp_type == "max"
                else daily["min_temperature"]
            )

            # -------------------------
            # 1) Background color cell
            # -------------------------
            fig.add_trace(
                go.Heatmap(
                    z=[[monthly_value]],
                    x=[0],
                    y=[0],
                    zmin=GLOBAL_MIN,
                    zmax=GLOBAL_MAX,
                    colorscale="YlOrRd",
                    showscale=(r == 0 and c == len(years) - 1),  # only once
                    colorbar=dict(
                        title="°C",
                        len=0.8
                    ),
                    hovertemplate=(
                        f"Year: {year}<br>"
                        f"Month: {calendar.month_name[month]}<br>"
                        f"Monthly {'Max' if temp_type=='max' else 'Min'}: "
                        f"{monthly_value:.1f}°C<extra></extra>"
                    ),
                ),
                row=r + 1,
                col=c + 1,
            )

            # -------------------------
            # 2) Mini daily line chart
            # -------------------------
            fig.add_trace(
                go.Scatter(
                    x=daily["day"],
                    y=y_values,
                    mode="lines",
                    line=dict(color="cyan", width=1.5),
                    showlegend=False,
                    hovertemplate=(
                        f"Date: {year}-{month:02d}-%{{x}}<br>"
                        "Temp: %{y:.1f}°C<extra></extra>"
                    ),
                ),
                row=r + 1,
                col=c + 1,
            )

    # -----------------------------
    # Clean mini-plot axes
    # -----------------------------
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    fig.update_layout(
        height=1000,
        width=1400,
        title=f"Monthly {'Maximum' if temp_type=='max' else 'Minimum'} Temperature (Last 10 Years)",
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return fig


# -----------------------------
# Dash App
# -----------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H2("Hong Kong Monthly Temperature Matrix"),

    html.Button(
        "Switch Max / Min",
        id="toggle-button",
        n_clicks=0
    ),

    dcc.Graph(id="matrix-graph")
])


# -----------------------------
# Toggle callback
# -----------------------------
@app.callback(
    Output("matrix-graph", "figure"),
    Input("toggle-button", "n_clicks")
)
def update_graph(n_clicks):

    temp_type = "max" if n_clicks % 2 == 0 else "min"
    return create_matrix(temp_type)


# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)