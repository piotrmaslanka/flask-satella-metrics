import os
import threading
import unittest

import flask
import requests
from satella.coding.sequences import choose
from satella.instrumentation.metrics import getMetric
from werkzeug.serving import run_simple

import flask_satella_metrics
from flask_satella_metrics.prometheus_exporter import PrometheusExporter

app = flask.Flask(__name__)
app.register_blueprint(PrometheusExporter({'service_name': 'my_service'}))
flask_satella_metrics.SatellaMetricsMiddleware(app)


@app.route('/', methods=['GET'])
def endpoint():
    return ''


@app.route('/value_error', methods=['GET'])
def value_error():
    raise ValueError()


class TestFlaskSatellaMetrics(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['FLASK_DEBUG'] = '1'
        thread = threading.Thread(
            target=lambda: run_simple('127.0.0.1', 5000, app, use_reloader=False), daemon=True)
        thread.start()

    def test_satella_metrics(self):
        getMetric('my.internal.metric', 'counter', internal=True)
        q = requests.get('http://localhost:5000/')
        self.assertEqual(q.status_code, 200)

        q = requests.get('http://localhost:5000/value_error')
        self.assertEqual(q.status_code, 500)

        root_metric = getMetric().to_metric_data()
        request_codes = choose(
            lambda metric: metric.name == 'requests_response_codes' and metric.labels == {
                'response_code': 200}, root_metric.values)
        self.assertEqual(request_codes.value, 1)
        request_codes = choose(
            lambda metric: metric.name == 'requests_response_codes' and metric.labels == {
                'response_code': 500}, root_metric.values)
        self.assertEqual(request_codes.value, 1)

        q = requests.get('http://localhost:5000/metrics')
        self.assertEqual(q.status_code, 200)
        self.assertIn('service_name="my_service"', q.text)
        self.assertIn('requests_response_codes', q.text)
        self.assertNotIn('my_internal_metric', q.text)
