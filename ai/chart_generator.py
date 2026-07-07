"""Auto-generate Plotly Charts."""

import pandas as pd
import plotly.express as px


def generate_chart(df: pd.DataFrame):
    if df.empty or len(df.columns) < 2:
        return None

    cols = df.columns
    # Classify columns
    date_cols = [
        c
        for c in cols
        if "date" in c.lower()
        or "dt" in c.lower()
        or "time" in c.lower()
        or "month" in c.lower()
        or "year" in c.lower()
    ]
    num_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    cat_cols = [c for c in cols if c not in date_cols and c not in num_cols]

    # 1. Time Series -> Line Chart
    if len(date_cols) >= 1 and len(num_cols) >= 1:
        # Sort by date for proper line rendering
        try:
            df = df.sort_values(by=date_cols[0])
        except Exception:
            pass
        if len(cat_cols) >= 1:
            return px.line(
                df,
                x=date_cols[0],
                y=num_cols[0],
                color=cat_cols[0],
                title="Trend Analysis over Time",
            )
        return px.line(
            df, x=date_cols[0], y=num_cols[0], title="Trend Analysis over Time"
        )

    # 2. Categorical vs Numeric -> Pie, Bar, or Geo Chart
    if len(cat_cols) >= 1 and len(num_cols) >= 1:
        x_col = cat_cols[0]
        y_col = num_cols[0]
        unique_vals = df[x_col].nunique()

        # Geographic
        if "country" in x_col.lower():
            return px.choropleth(
                df,
                locations=x_col,
                locationmode="country names",
                color=y_col,
                title=f"Geographic Distribution of {y_col}",
            )

        # Pie Chart
        if unique_vals <= 7 and (df[y_col] >= 0).all():
            return px.pie(
                df, names=x_col, values=y_col, title=f"Proportion Analysis of {y_col}"
            )

        # Bar Chart
        if len(cat_cols) > 1:
            return px.bar(
                df,
                x=x_col,
                y=y_col,
                color=cat_cols[1],
                title=f"Distribution of {y_col} by {x_col}",
                barmode="group",
            )

        # Sort values for a cleaner bar chart if there are many categories
        if unique_vals > 7:
            df = df.sort_values(by=y_col, ascending=False).head(
                20
            )  # Limit to top 20 for readability

        return px.bar(df, x=x_col, y=y_col, title=f"Distribution of {y_col} by {x_col}")

    # 3. Numeric vs Numeric -> Scatter Plot
    if len(num_cols) >= 2:
        color_args = {"color": cat_cols[0]} if len(cat_cols) >= 1 else {}
        return px.scatter(
            df,
            x=num_cols[0],
            y=num_cols[1],
            title=f"Correlation between {num_cols[0]} and {num_cols[1]}",
            **color_args,
        )

    return None
