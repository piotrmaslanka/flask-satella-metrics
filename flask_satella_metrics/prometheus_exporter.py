import logging
import typing as tp

from flask import Blueprint
from satella.instrumentation.metrics.exporters import metric_data_collection_to_prometheus
from satella.instrumentation.metrics import getMetric

logger = logging.getLogger(__name__)


def PrometheusExporter(extra_labels: tp.Optional[dict] = None) -> Blueprint:
    labels = extra_labels or {}

    blueprint = Blueprint('prometheus_exporter', __name__)

    @blueprint.route('/metrics', methods=['GET'])
    def export_prometheus():
        metric = getMetric()
        metric_data = metric.to_metric_data()
        metric_data.add_labels(labels)
        return metric_data_collection_to_prometheus(metric_data)

    return blueprint