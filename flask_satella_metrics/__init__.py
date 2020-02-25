import time
import typing as tp
from collections import namedtuple

import flask
from satella.time import measure
from satella.instrumentation.metrics import getMetric, Metric

__version__ = '1.3'

__all__ = ['SatellaMetricsMiddleware']

MetricsContainer = namedtuple('MetricsContainer', ['summary_metric',
                                                   'histogram_metric',
                                                   'response_codes_metric'])


def SatellaMetricsMiddleware(app: flask.Flask, summary_metric: tp.Optional[Metric] = None,
                             histogram_metric: tp.Optional[Metric] = None,
                             response_codes_metric: tp.Optional[Metric] = None):
    """
    Install handlers to measure metrics on an application

    :param app: flask application to monitor
    :param summary_metric: summary metric to use. Should be of type 'summary'
    :param histogram_metric: histogram metric to use. Should be of type 'histogram'
    :param response_codes_metric: Response codes counter to use. Should be of type 'counter'
    """
    app.metrics = MetricsContainer(
        summary_metric or getMetric('requests_summary', 'summary',
                                    quantiles=[0.2, 0.5, 0.9, 0.95, 0.99]),
        histogram_metric or getMetric('requests_histogram', 'histogram'),
        response_codes_metric or getMetric('requests_response_codes', 'counter'))
    app.before_request(before_request)
    app.after_request(after_request)


def before_request():
    flask.request.time_measure = measure()


def after_request(response):
    time_measure = flask.request.time_measure
    time_measure.stop()
    elapsed = time_measure()
    endpoint = str(flask.request.endpoint)
    flask.current_app.metrics.summary_metric.runtime(elapsed, endpoint=endpoint)
    flask.current_app.metrics.histogram_metric.runtime(elapsed, endpoint=endpoint)
    flask.current_app.metrics.response_codes_metric.runtime(+1, response_code=response.status_code)
    return response
