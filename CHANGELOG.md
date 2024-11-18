# v1.6.0

* streaming responses times will now be calculated correctly

# v1.5.1

* fixed not exporting internal metrics

# v1.5

* added optional `url` for `PrometheusExporter`

# v1.4

* internal metrics won't be exported anymore

# v1.3

* refactored to use `satella.time.measure` to measure elapsed time

# v1.2

* bugfix: earlier `flask-satella-metrics` would not register
  calls that ended with an exception

# v1.1

* added `PrometheusExporter`