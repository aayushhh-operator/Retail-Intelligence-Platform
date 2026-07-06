"""Validation report generation for JSON, CSV, HTML, and dashboard summaries."""

from __future__ import annotations

import csv
import html
from pathlib import Path
from typing import Any

from config.pipeline_run import get_pipeline_run_id
from validate.utils import write_json


class ValidationReportGenerator:
    """Generate validation reports for downstream observability."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.dataset_dir = output_dir / "dataset_reports"

    def write_all(self, reports: list[dict[str, Any]], recommendation: dict[str, str]) -> dict[str, Path]:
        """Write all validation report artifacts."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        for report in reports:
            write_json(self.dataset_dir / f"{report['dataset']}.json", report)

        summary = self._summary(reports, recommendation)
        dashboard = self._dashboard_summary(reports, summary)
        paths = {
            "summary": self.output_dir / "validation_summary.json",
            "csv": self.output_dir / "validation_report.csv",
            "html": self.output_dir / "validation_report.html",
            "dashboard": self.output_dir / "data_quality_dashboard.json",
        }
        write_json(paths["summary"], summary)
        write_json(paths["dashboard"], dashboard)
        self._write_csv(paths["csv"], reports)
        self._write_html(paths["html"], reports, summary)
        return paths

    def _summary(self, reports: list[dict[str, Any]], recommendation: dict[str, str]) -> dict[str, Any]:
        passed = sum(1 for report in reports if report["status"] == "PASS")
        warning = sum(1 for report in reports if report["status"] == "WARNING")
        failed = sum(1 for report in reports if report["status"] == "FAIL")
        overall = round(sum(float(report["quality_score"]) for report in reports) / len(reports), 2) if reports else 0.0
        return {
            "pipeline_run_id": get_pipeline_run_id(),
            "datasets": len(reports),
            "passed": passed,
            "warning": warning,
            "failed": failed,
            "overall_quality": overall,
            "recommendation": recommendation,
        }

    def _dashboard_summary(self, reports: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "pipeline_run_id": get_pipeline_run_id(),
            "overall_quality": summary["overall_quality"],
            "datasets": [
                {
                    "name": report["dataset"],
                    "score": report["quality_score"],
                    "status": report["status"],
                    "errors": report["errors"],
                    "warnings": report["warnings"],
                }
                for report in reports
            ],
        }

    def _write_csv(self, path: Path, reports: list[dict[str, Any]]) -> None:
        fieldnames = ["Dataset", "Rows", "Columns", "Errors", "Warnings", "Quality Score", "Status", "Execution Time"]
        with path.open("w", encoding="utf-8", newline="") as file_obj:
            writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
            writer.writeheader()
            for report in reports:
                writer.writerow(
                    {
                        "Dataset": report["dataset"],
                        "Rows": report["rows"],
                        "Columns": report["columns"],
                        "Errors": report["errors"],
                        "Warnings": report["warnings"],
                        "Quality Score": report["quality_score"],
                        "Status": report["status"],
                        "Execution Time": report["execution_time_seconds"],
                    }
                )

    def _write_html(self, path: Path, reports: list[dict[str, Any]], summary: dict[str, Any]) -> None:
        rows = "\n".join(
            "<tr>"
            f"<td>{html.escape(report['dataset'])}</td>"
            f"<td>{report['rows']}</td>"
            f"<td>{report['columns']}</td>"
            f"<td>{report['errors']}</td>"
            f"<td>{report['warnings']}</td>"
            f"<td><strong>{report['quality_score']}</strong></td>"
            f"<td><span class='status {report['status'].lower()}'>{report['status']}</span></td>"
            "</tr>"
            for report in reports
        )
        issue_sections = "\n".join(self._issue_section(report) for report in reports)
        path.write_text(
            f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Retail Intelligence Validation Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; background: #f8fafc; }}
    h1, h2 {{ color: #111827; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }}
    .metric {{ font-size: 28px; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: white; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }}
    th {{ background: #eef2f7; }}
    .status {{ padding: 4px 8px; border-radius: 4px; font-weight: 700; }}
    .pass {{ background: #dcfce7; color: #166534; }}
    .warning {{ background: #fef3c7; color: #92400e; }}
    .fail {{ background: #fee2e2; color: #991b1b; }}
    .issues {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-top: 16px; }}
    code {{ color: #334155; }}
  </style>
</head>
<body>
  <h1>Retail Intelligence Data Quality Report</h1>
  <p><strong>Pipeline run:</strong> <code>{html.escape(summary['pipeline_run_id'])}</code></p>
  <div class="cards">
    <div class="card"><div>Overall Quality</div><div class="metric">{summary['overall_quality']}</div></div>
    <div class="card"><div>Passed</div><div class="metric">{summary['passed']}</div></div>
    <div class="card"><div>Warning</div><div class="metric">{summary['warning']}</div></div>
    <div class="card"><div>Failed</div><div class="metric">{summary['failed']}</div></div>
  </div>
  <h2>Dataset Summary</h2>
  <table>
    <thead><tr><th>Dataset</th><th>Rows</th><th>Columns</th><th>Errors</th><th>Warnings</th><th>Quality</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Recommendation</h2>
  <p><strong>{html.escape(summary['recommendation']['decision'])}</strong>: {html.escape(summary['recommendation']['reason'])}</p>
  <h2>Validation Failures</h2>
  {issue_sections}
</body>
</html>
""",
            encoding="utf-8",
        )

    def _issue_section(self, report: dict[str, Any]) -> str:
        issues = report.get("detected_issues", [])
        if not issues:
            return f"<div class='issues'><h3>{html.escape(report['dataset'])}</h3><p>No validation issues detected.</p></div>"
        items = "".join(
            f"<li><strong>{html.escape(issue['rule_name'])}</strong>: {html.escape(issue['message'])}</li>"
            for issue in issues[:10]
        )
        return f"<div class='issues'><h3>{html.escape(report['dataset'])}</h3><ul>{items}</ul></div>"

