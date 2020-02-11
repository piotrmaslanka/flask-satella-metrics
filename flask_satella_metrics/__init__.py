import typing as tp
from satella.instrumentation.metrics import getMetric, Metric
from satella.coding import static_var
import flask
import threading
import time

__version__ = '0.1a1'


@static_var('summary_metric', None)
@static_var('histogram_metric', None)
@static_var('response_codes_metric', None)
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
    SatellaMetricsMiddleware.summary_metric = summary_metric or \
                                              getMetric('requests_summary', 'summary',
                                                        quantiles=[0.2, 0.5, 0.9, 0.95, 0.99])
    SatellaMetricsMiddleware.histogram_metric = histogram_metric or \
                                                getMetric('requests_histogram', 'histogram')
    SatellaMetricsMiddleware.response_codes_metric = response_codes_metric or \
                                                     getMetric('requests_response_codes',
                                                               'counter')
    app.before_request(before_request)
    app.after_request(after_request)


def before_request():
    flask.request.start_time = time.monotonic()


def after_request(response):
    elapsed = time.monotonic() - flask.request.start_time
    endpoint = str(flask.request.endpoint)
    SatellaMetricsMiddleware.summary_metric.runtime(elapsed, endpoint=endpoint)
    SatellaMetricsMiddleware.histogram_metric.runtime(elapsed, endpoint=endpoint)
    SatellaMetricsMiddleware.response_codes_metric.runtime(+1, response_code=response.status_code)
    return response
