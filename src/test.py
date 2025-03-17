import gevent
import requests

def _submit_wrapper(urls, job_name, metric_name, metric_value, dimensions):
    dim = ''
    headers = {'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
    for key, value in dimensions.iteritems():
        dim += '/%s/%s' % (key, value)
    for url in urls:
        requests.post('http://%s/metrics/job/%s%s' % (url, job_name, dim),
                      data='%s %s\n' % (metric_name, metric_value), headers=headers)


def submit_metrics(job_name, metric_name, metric_value, dimensions={}):
    from ..app import config
    cfg = config.init()
    urls = cfg['PUSHGATEWAY_URLS'].split(',')
    gevent.spawn(_submit_wrapper, urls, job_name, metric_name, metric_value, dimensions)