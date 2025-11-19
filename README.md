# FILE: README.md

# Website Uptime Monitor

A production-style website uptime monitoring system that checks URL availability and response times, exposing metrics via Prometheus and visualizing them in Grafana.

## Tech Stack

- Python 3.10+
- Requests
- Prometheus Client Library
- Docker
- Docker Compose
- Prometheus
- Grafana

## Prerequisites

- Docker
- Docker Compose

## How to Run

Start all services:

```bash
docker-compose up --build
```

Access the services:

- Grafana: http://localhost:3000 (login: admin/admin)
- Prometheus: http://localhost:9090
- Monitor Metrics: http://localhost:8000/metrics

## Grafana Dashboard

The uptime monitoring dashboard is automatically provisioned on startup. After logging into Grafana with the default credentials (admin/admin), you can find the "Website Uptime Monitor" dashboard in the dashboard list.

The dashboard displays:
- Real-time uptime status for all monitored URLs
- Historical uptime trends

## Configuration

Edit `app/config.py` to:

- Change the list of URLs to monitor (`URLS`)
- Adjust the check interval (`CHECK_INTERVAL_SECONDS`)

## How It Works

1. The monitor service periodically checks each configured URL via HTTP GET requests.
2. For each check, it records availability (up/down) and response time as Prometheus metrics.
3. Prometheus scrapes these metrics from the monitor service every 10 seconds.
4. Grafana connects to Prometheus as a data source and visualizes the metrics in dashboards.

## Metrics

- `website_up`: Gauge indicating if a website is up (1) or down (0), labeled by URL.
- `website_response_time_seconds`: Histogram of response times in seconds, labeled by URL.
