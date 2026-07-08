# Streamlit Analytics Dashboard (Enterprise UX Edition)

This directory contains the Streamlit-based web application that acts as the front-end Business Intelligence and observability layer for the Retail Intelligence Platform.

## Theming & UI Framework
The dashboard was heavily customized to emulate premium, enterprise-grade BI tools (Power BI, Looker, etc.).

### Component Hierarchy
To avoid scattered inline styles, the UI is broken into modular components:
- `components/layout.py`: Injects custom CSS, defines standard grid layouts, and renders headers.
- `components/cards.py`: Reusable, animated KPI metric cards with built-in trend indicators.
- `components/charts.py`: Centralized Plotly wrappers that enforce corporate color palettes, remove gridlines, and lock margins.
- `components/filters.py`: Global sidebar filtering systems.
- `components/states.py`: Fallback UI components (loading spinners, empty state illustrations, error tracebacks).
- `styles/theme.css`: The core stylesheet overriding Streamlit's default padding, typography, and card behaviors.

### Theming
The dashboard supports Dark and Light mode automatically based on the user's OS preference. You can manually force a theme by going to the top-right Streamlit settings menu > Settings > Theme.

## Pages
1. **Overview**: High-level business KPIs.
2. **Sales Analysis**: Deep dive into revenue and category performance.
3. **Customer Insights**: Segmentation and Customer Lifetime Value (CLV).
4. **Product Performance**: Inventory and top sellers.
5. **Operations Monitoring**: Supply chain and warehouse status.
6. **Pipeline Health**: Airflow orchestration observability, showing DAG and Task execution success rates.
7. **Spark Analytics**: Visualization of heavy Spark workloads (like sessionization and event funnels).
8. **AI Copilot**: A fully functional conversational UI with side-by-side SQL generation and charting.
9. **Settings**: Application preferences and cache clearing.

## How to Run

```bash
make dashboard
```
*(Or manually via `streamlit run dashboard/app.py`)*
