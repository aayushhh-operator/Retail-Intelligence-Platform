"""Transformation pipeline execution for a single dataset.

This module defines the ``TransformationPipeline`` class which wraps a
``BaseTransformer`` and provides a clean execution boundary. Each pipeline
instance is responsible for one dataset only, following the Single
Responsibility Principle.

The ``TransformationPipelineRunner`` coordinates multiple pipelines and
aggregates their results, which is what ``transformation_manager.py`` uses.
"""

from __future__ import annotations

import logging
from pathlib import Path

from transform.base_transformer import BaseTransformer
from transform.config import TRANSFORMATION_CONFIG, TransformationConfig
from transform.metrics import TransformationMetrics
from transform.registry import TransformerRegistry, build_default_registry


class TransformationPipeline:
    """Execution wrapper for one dataset transformation.

    Separates execution concerns (paths, logging, error handling) from
    transformation logic (cleaning, imputing, enriching) which lives in
    ``BaseTransformer`` and its subclasses.
    """

    def __init__(
        self,
        transformer: BaseTransformer,
        validation_log_dir: Path,
    ) -> None:
        self.transformer = transformer
        self.validation_log_dir = validation_log_dir

    def execute(self) -> TransformationMetrics:
        """Run the transformer and return collected metrics."""
        return self.transformer.run(self.validation_log_dir)


class TransformationPipelineRunner:
    """Coordinate transformation pipelines across multiple datasets.

    The runner instantiates one ``TransformationPipeline`` per registered
    dataset, executes them sequentially, and returns the full list of metrics.
    A failure in one dataset does not abort the others.
    """

    def __init__(
        self,
        raw_dir: Path,
        processed_dir: Path,
        validation_log_dir: Path,
        transform_report_dir: Path,
        registry: TransformerRegistry | None = None,
        config: TransformationConfig | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.validation_log_dir = validation_log_dir
        self.transform_report_dir = transform_report_dir
        self.registry = registry or build_default_registry()
        self.config = config or TRANSFORMATION_CONFIG
        self.logger = logger or logging.getLogger("transform.runner")

    def run(self) -> list[TransformationMetrics]:
        """Execute every registered dataset transformer and return metrics."""
        # Dataset definitions: (name, filename, primary_key)
        dataset_definitions = [
            ("customers", "customers.csv", "customer_id"),
            ("products", "products.csv", "id"),
            ("inventory", "inventory.csv", "inventory_id"),
            ("orders", "orders.csv", "order_id"),
            ("payments", "payments.csv", "payment_id"),
            ("shipping", "shipping.csv", "shipping_id"),
            ("reviews", "reviews.csv", "review_id"),
            ("website_events", "website_events.json", "event_id"),
        ]

        all_metrics: list[TransformationMetrics] = []

        for dataset_name, filename, primary_key in dataset_definitions:
            raw_path = self.raw_dir / filename
            if not raw_path.is_file():
                self.logger.warning("%s | raw file not found: %s — skipping", dataset_name, raw_path)
                skipped = TransformationMetrics(dataset=dataset_name, status="SKIPPED", error_message=f"Raw file not found: {raw_path}")
                all_metrics.append(skipped)
                continue

            transformer = self.registry.create(
                dataset=dataset_name,
                raw_path=raw_path,
                processed_dir=self.processed_dir,
                transform_report_dir=self.transform_report_dir,
                config=self.config,
                logger=self.logger.getChild(dataset_name),
                primary_key=primary_key,
            )
            pipeline = TransformationPipeline(
                transformer=transformer,
                validation_log_dir=self.validation_log_dir,
            )
            self.logger.info("%s | pipeline started", dataset_name)
            metrics = pipeline.execute()
            all_metrics.append(metrics)
            self.logger.info(
                "%s | pipeline completed status=%s rows_out=%d",
                dataset_name,
                metrics.status,
                metrics.rows_output,
            )

        return all_metrics
