# FILE: app/monitor.py

import logging
import time
import requests
from prometheus_client import start_http_server

from app.config import URLS, CHECK_INTERVAL_SECONDS
from app.metrics import set_website_up, observe_response_time


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting Prometheus metrics server on port 8000")
    start_http_server(8000)

    logger.info(f"Monitoring {len(URLS)} URLs with {CHECK_INTERVAL_SECONDS}s interval")

    while True:
        for url in URLS:
            start_time = time.time()
            try:
                response = requests.get(url, timeout=5)
                elapsed = time.time() - start_time

                if response.status_code < 500:
                    set_website_up(url, True)
                    observe_response_time(url, elapsed)
                    logger.info(f"{url} - UP (status={response.status_code}, time={elapsed:.3f}s)")
                else:
                    set_website_up(url, False)
                    logger.warning(f"{url} - DOWN (status={response.status_code})")
            except Exception as e:
                set_website_up(url, False)
                logger.error(f"{url} - DOWN (error={str(e)})")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
