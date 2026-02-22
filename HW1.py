import pandas as pd
import calendar
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("temperature_daily.csv", parse_dates=["date"])

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day

# using the last 10 years
last_year = df["year"].max()
df = df[df["year"] >= last_year - 9]

years = sorted(df["year"].unique())
months = list(range(1, 13))

# monthly summaries
monthly_max = df.groupby(["year", "month"])["max_temperature"].max().unstack()
monthly_min = df.groupby(["year", "month"])["min_temperature"].min().unstack()

GLOBAL_MIN = df["min_temperature"].min()
GLOBAL_MAX = df["max_temperature"].max()

# -----------------------------
# Create subplot matrix
# -----------------------------
fig = make_subplots(
    rows=12,
    cols=len(years),
    horizontal_spacing=0.002,
    vertical_spacing=0.01,
    row_titles=[calendar.month_abbr[m] for m in months],  # Short month labels to p
    column_titles=[str(y) for y in years],
)

max_visibility = []
min_visibility = []

# -----------------------------
# Populate cells
# -----------------------------
for r, month in enumerate(months):
    for c, year in enumerate(years):

        max_val = monthly_max.loc[year, month]
        min_val = monthly_min.loc[year, month]

        daily = df[(df.year == year) & (df.month == month)]

        # ========= MAX MODE =========

        heat_max = go.Heatmap(
            z=[[max_val]],
            zmin=GLOBAL_MIN,
            zmax=GLOBAL_MAX,
            colorscale="YlOrRd",
            showscale=(r == 0 and c == len(years) - 1),  # show legend once
            hovertemplate=(
                f"Year: {year}<br>"
                f"Month: {calendar.month_name[month]}<br>"
                f"Monthly Max: {max_val:.1f}°C<extra></extra>"
            ),
            visible=True,
        )

        line_max = go.Scatter(
            x=daily["day"],
            y=daily["max_temperature"],
            mode="lines",
            line=dict(color="cyan", width=1.5),
            showlegend=False,
            hovertemplate=(
                f"Date: {year}-{month:02d}-%{{x}}<br>"
                "Max Temp: %{y:.1f}°C<extra></extra>"
            ),
            visible=True,
        )

        # ========= MIN MODE =========

        heat_min = go.Heatmap(
            z=[[min_val]],
            zmin=GLOBAL_MIN,
            zmax=GLOBAL_MAX,
            colorscale="YlOrRd",
            showscale=False,
            hovertemplate=(
                f"Year: {year}<br>"
                f"Month: {calendar.month_name[month]}<br>"
                f"Monthly Min: {min_val:.1f}°C<extra></extra>"
            ),
            visible=False,
        )

        line_min = go.Scatter(
            x=daily["day"],
            y=daily["min_temperature"],
            mode="lines",
            line=dict(color="cyan", width=1.5),
            showlegend=False,
            hovertemplate=(
                f"Date: {year}-{month:02d}-%{{x}}<br>"
                "Min Temp: %{y:.1f}°C<extra></extra>"
            ),
            visible=False,
        )

        # adding traces
        fig.add_trace(heat_max, row=r + 1, col=c + 1)
        fig.add_trace(line_max, row=r + 1, col=c + 1)
        fig.add_trace(heat_min, row=r + 1, col=c + 1)
        fig.add_trace(line_min, row=r + 1, col=c + 1)

        # Track visibility for toggle
        max_visibility += [True, True, False, False]
        min_visibility += [False, False, True, True]

fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)

# -----------------------------
# Layout + Toggle Buttons
# -----------------------------
fig.update_layout(
    title="Hong Kong Monthly Temperature Matrix",
    height=1000,
    width=1400,

    #prevents label overlap & cell distortion
    margin=dict(l=90, r=20, t=80, b=20),

    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            x=0.5,
            y=1.08,
            xanchor="center",
            buttons=[
                dict(
                    label="Maximum Temperature",
                    method="update",
                    args=[{"visible": max_visibility}],
                ),
                dict(
                    label="Minimum Temperature",
                    method="update",
                    args=[{"visible": min_visibility}],
                ),
            ],
        )
    ],
)

# -----------------------------
# Show + Save
# -----------------------------
fig.show()
fig.write_html("matrix_view.html")