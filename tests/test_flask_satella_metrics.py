import logging
import typing as tp
import unittest
import flask
import os
from werkzeug.serving import run_simple
import threading
import requests
from satella.instrumentation.metrics import getMetric
from satella.coding.sequences import choose
from flask_satella_metrics import SatellaMetricsMiddleware
logger = logging.getLogger(__name__)


app = flask.Flask(__name__)
SatellaMetricsMiddleware(app)


@app.route('/', methods=['GET'])
def endpoint():
    return ''


class TestFlaskSatellaMetrics(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['FLASK_DEBUG'] = '1'
        thread = threading.Thread(target=lambda: run_simple('127.0.0.1', 5000, app, use_reloader=False), daemon=True)
        thread.start()

    def test_satella_metrics(self):
        q = requests.get('http://localhost:5000/')
        logger.warning(f'{q.text}')
        self.assertEqual(q.status_code, 200)

        root_metric = getMetric().to_metric_data()
        logger.warning(f'{root_metric.values}')
        request_codes = choose(lambda metric: metric.name == 'requests_response_codes' and metric.labels == {'response_code': 200}, root_metric.values)
        self.assertEqual(request_codes.value, 1)
