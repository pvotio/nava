import requests
from django.conf import settings
from requests.adapters import HTTPAdapter, Retry

session = requests.Session()
retries = Retry(
    total=settings.REQUEST_MAX_RETRIES,
    backoff_factor=settings.REQUEST_BACKOFF_FACTOR,
    status_forcelist=[500, 502, 503, 504],
)

session.mount("http://generator:3000", HTTPAdapter(max_retries=retries))
