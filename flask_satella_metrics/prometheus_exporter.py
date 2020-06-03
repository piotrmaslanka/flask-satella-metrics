import logging
import typing as tp

from flask import Blueprint
from satella.instrumentation.metrics import getMetric
from satella.instrumentation.metrics.exporters import metric_data_collection_to_prometheus

logger = logging.getLogger(__name__)


def PrometheusExporter(extra_labels: tp.Optional[dict] = None,
                       url: str = '/metrics') -> Blueprint:
    labels = extra_labels or {}

    blueprint = Blueprint('prometheus_exporter', __name__)

    @blueprint.route(url, methods=['GET'])
    def export_prometheus():
        metric = getMetric()
        metric_data = metric.to_metric_data()
        for datum in metric_data.values:
            if datum.internal:
                metric_data.values.remove(datum)
        metric_data.add_labels(labels)
        return metric_data_collection_to_prometheus(metric_data)

    return blueprint
