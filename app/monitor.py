# FILE: app/monitor.py

import logging
import time
import requests
from prometheus_client import start_http_server

from app.config import CHECK_INTERVAL_SECONDS
from app.metrics import set_website_up, observe_response_time, remove_url_metrics
from app.database import SessionLocal, init_db
from app.models import MonitoredURL, User


def get_active_urls():
    """Fetch all active URLs from database with user information"""
    db = SessionLocal()
    try:
        urls = db.query(MonitoredURL, User).join(User).filter(
            MonitoredURL.is_active == True
        ).all()
        return [(monitored_url.url, monitored_url.user_id, user.username)
                for monitored_url, user in urls]
    finally:
        db.close()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize database
    init_db()
    logger.info("Database initialized")

    logger.info("Starting Prometheus metrics server on port 8000")
    start_http_server(8000)

    logger.info(f"Starting URL monitoring with {CHECK_INTERVAL_SECONDS}s interval")

    # Track URLs from previous iteration to detect removals
    previous_urls = set()

    while True:
        # Fetch active URLs from database on each iteration
        urls_to_monitor = get_active_urls()
        current_urls = set(urls_to_monitor)

        # Detect removed URLs and clean up their metrics
        removed_urls = previous_urls - current_urls
        for url, user_id, username in removed_urls:
            logger.info(f"Removing metrics for [{username}] {url}")
            remove_url_metrics(url, user_id, username)

        previous_urls = current_urls

        if not urls_to_monitor:
            logger.info("No active URLs to monitor")
        else:
            logger.debug(f"Monitoring {len(urls_to_monitor)} URLs")

        for url, user_id, username in urls_to_monitor:
            start_time = time.time()
            try:
                response = requests.get(url, timeout=5)
                elapsed = time.time() - start_time

                if response.status_code < 500:
                    set_website_up(url, True, user_id, username)
                    observe_response_time(url, elapsed, user_id, username)
                    logger.info(f"[{username}] {url} - UP (status={response.status_code}, time={elapsed:.3f}s)")
                else:
                    set_website_up(url, False, user_id, username)
                    logger.warning(f"[{username}] {url} - DOWN (status={response.status_code})")
            except Exception as e:
                set_website_up(url, False, user_id, username)
                logger.error(f"[{username}] {url} - DOWN (error={str(e)})")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
