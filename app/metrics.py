# FILE: app/metrics.py

from prometheus_client import Gauge, Histogram

website_up = Gauge('website_up', 'Website availability (1=up, 0=down)', ['url', 'user_id', 'username'])
website_response_time_seconds = Histogram('website_response_time_seconds', 'Website response time in seconds', ['url', 'user_id', 'username'])


def set_website_up(url: str, up: bool, user_id: int, username: str) -> None:
    website_up.labels(url=url, user_id=str(user_id), username=username).set(1 if up else 0)


def observe_response_time(url: str, seconds: float, user_id: int, username: str) -> None:
    website_response_time_seconds.labels(url=url, user_id=str(user_id), username=username).observe(seconds)


def remove_url_metrics(url: str, user_id: int, username: str) -> None:
    """Remove metrics for a URL by clearing its labels from the collectors"""
    try:
        website_up.remove(url, str(user_id), username)
    except KeyError:
        pass  # Metric doesn't exist, ignore

    try:
        website_response_time_seconds.remove(url, str(user_id), username)
    except KeyError:
        pass  # Metric doesn't exist, ignore
