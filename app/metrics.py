# FILE: app/metrics.py

from prometheus_client import Gauge, Histogram

website_up = Gauge('website_up', 'Website availability (1=up, 0=down)', ['url'])
website_response_time_seconds = Histogram('website_response_time_seconds', 'Website response time in seconds', ['url'])


def set_website_up(url: str, up: bool) -> None:
    website_up.labels(url=url).set(1 if up else 0)


def observe_response_time(url: str, seconds: float) -> None:
    website_response_time_seconds.labels(url=url).observe(seconds)
