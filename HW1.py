import pandas as pd
import plotly.graph_objects as go

# =========================
# 1. LOAD DATA
# =========================
df = pd.read_csv("temperature_daily.csv")
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day

# =========================
# 2. FILTER LAST 10 YEARS
# =========================
last_year = df["year"].max()
start_year = last_year - 9
df = df[df["year"] >= start_year]

# =========================
# 3. BUILD MONTHLY CELLS
# =========================
monthly = (
    df.groupby(["year", "month"])
        .agg(
            avg_temp=("max_temperature", "mean"),
            max_series=("max_temperature", list),
            min_series=("min_temperature", list),
            day_series=("day", list)
        )
        .reset_index()
)

# =========================
# 4. HEATMAP MATRIX
# =========================
heat = monthly.pivot(index="month", columns="year", values="avg_temp")
years = list(heat.columns)
months = list(heat.index)

# =========================
# 5. CREATE FIGURE
# =========================
fig = go.Figure()

fig.add_trace(
    go.Heatmap(
        z=heat.values,
        x=years,
        y=months,
        colorscale="RdYlBu_r",
        colorbar_title="Avg Temp"
    )
)

# =========================
# 6. MINI LINES WITH DAY/TEMP HOVER
# =========================
max_traces = []
min_traces = []

for _, row in monthly.iterrows():
    days = row["day_series"]

    # Max temperatures
    temps = row["max_series"]
    tmin, tmax = min(temps), max(temps)
    x_offset = [d/31 for d in days]
    x_vals = [row["year"] + o*0.8 - 0.4 for o in x_offset]
    y_offset = [(t-tmin)/(tmax-tmin+1e-6) for t in temps]
    y_vals = [row["month"] + o*0.8 - 0.4 for o in y_offset]

    hover_text = [f"{row['year']}-{row['month']:02d}-{d:02d}: {t}°C" for d, t in zip(days, temps)]

    max_traces.append(go.Scatter(
        x=x_vals, y=y_vals, mode="lines",
        line=dict(width=1, color="orange"),
        showlegend=False, visible=True,
        hoverinfo="text", hovertext=hover_text
    ))

    # Min temperatures
    temps = row["min_series"]
    tmin, tmax = min(temps), max(temps)
    y_offset = [(t-tmin)/(tmax-tmin+1e-6) for t in temps]
    y_vals = [row["month"] + o*0.8 - 0.4 for o in y_offset]

    hover_text = [f"{row['year']}-{row['month']:02d}-{d:02d}: {t}°C" for d, t in zip(days, temps)]

    min_traces.append(go.Scatter(
        x=x_vals, y=y_vals, mode="lines",
        line=dict(width=1, color="cyan"),
        showlegend=False, visible=False,
        hoverinfo="text", hovertext=hover_text
    ))

for t in max_traces + min_traces:
    fig.add_trace(t)

# =========================
# 7. YEAR TITLES
# =========================
annotations = [dict(x=y, y=13.5, text=str(y), showarrow=False, font=dict(size=14)) for y in years]

# =========================
# 8. TOGGLE BUTTON ATTACHED TO TITLE
# =========================
n = len(max_traces)
visibility_max = [True]+[True]*n+[False]*n
visibility_min = [True]+[False]*n+[True]*n

fig.update_layout(
    updatemenus=[dict(
        buttons=[
            dict(label="Max", method="update", args=[{"visible": visibility_max}]),
            dict(label="Min", method="update", args=[{"visible": visibility_min}])
        ],
        direction="right",
        x=0.5,          # start near center
        y=1.05,         # slightly above the top of the figure canvas
        xanchor='left', # anchor left side of button to this x
        yanchor='middle',
        pad=dict(l=10,b=0,t=0,r=0)
    )]
)

# =========================
# 9. TITLE + AXES
# =========================
fig.update_layout(
    title=dict(
        text="Monthly Average Temperatures (Last 10 Years)",
        x=0.5, xanchor='center', y=0.85, yanchor='middle', font=dict(size=20)
    ),
    xaxis_title="Year",
    yaxis_title="Month",
    yaxis=dict(
        tickmode="array",
        tickvals=list(range(1,13)),
        ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    ),
    height=750,
    annotations=annotations
)

# =========================
# 10. SHIFT FIGURE DOWN
# =========================
fig.update_layout(
    margin=dict(t=180, b=80, l=80, r=80)
)

fig.show()
