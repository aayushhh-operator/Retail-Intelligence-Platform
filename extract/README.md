# Extraction Layer

The `extract` package implements Phase 2 of the Retail Intelligence Platform: reliable ingestion from independent upstream systems into raw storage.

This layer does not validate, clean, transform, model, or load data into a database. Its only responsibility is to copy or fetch source data into `data/raw/` while producing operational metadata.

## Architecture

- `extractor.py`: base extractor contract and shared execution flow.
- `csv_extractor.py`: streams CSV files from `data/source/` into `data/raw/`.
- `json_extractor.py`: copies JSON or NDJSON files into `data/raw/`.
- `api_extractor.py`: downloads HTTP API responses and stores raw JSON.
- `registry.py`: maps source types to extractor classes and defines Phase 2 sources.
- `ingestion_manager.py`: runs all configured extractors and writes the manifest.
- `metadata.py`: serializes dataset metadata and run manifests.
- `utils.py`: checksum, copy, and lightweight file inspection helpers.
- `exceptions.py`: extraction-specific exceptions.

## Supported Source Types

- CSV: UTF-8 files with quoted value support through Python's CSV parser.
- JSON: standard JSON files, including list and dictionary payloads.
- NDJSON: newline-delimited JSON records.
- API: HTTP GET endpoints saved as raw JSON.

## Current Sources

| Dataset | Source Type | Upstream |
| --- | --- | --- |
| customers | CSV | `data/source/customers.csv` |
| inventory | CSV | `data/source/inventory.csv` |
| orders | CSV | `data/source/orders.csv` |
| payments | CSV | `data/source/payments.csv` |
| reviews | CSV | `data/source/reviews.csv` |
| shipping | CSV | `data/source/shipping.csv` |
| products | API | `https://fakestoreapi.com/products` |
| website_events | JSON | `data/source/website_events.json` |

`website_events.json` is registered for Phase 2 ingestion even if the upstream file is not present yet. The manager records a failed metadata entry and continues ingesting other datasets.

## How To Run

From the project root:

```bash
python pipeline.py
```

Or run the ingestion layer directly:

```bash
python extract/ingestion_manager.py
```

## Metadata

Each dataset writes a metadata file to `logs/metadata/`.

Each metadata file includes:

- `pipeline_run_id`
- dataset name
- source type
- original path
- destination path
- row count
- columns
- file size
- extraction timestamp
- execution time
- SHA256 checksum
- status
- error message when extraction fails

The complete run writes `logs/ingestion_manifest.json`, which includes the same `pipeline_run_id` and a summary of succeeded and failed datasets.

## Pipeline Run ID

Every execution creates an identifier such as `RUN_20260706_143522`. Logs, metadata, and manifest files include this value so future validation reports, transformation reports, warehouse loads, and dashboard metrics can be tied back to the same pipeline execution.

## Adding A New Source

1. Add a `SourceConfig` entry in `registry.py`.
2. Reuse an existing source type or register a new extractor class.
3. Keep extractor behavior limited to ingestion and raw persistence.
4. Add tests for the extractor or registry behavior.

## Logging

The ingestion layer uses the project logging configuration from Phase 0. Logs include the active `pipeline_run_id`, dataset start and finish events, row counts, execution time, errors, and pipeline completion.

