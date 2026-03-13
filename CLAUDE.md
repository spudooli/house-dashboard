# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Spudooli House Dashboard is a personal home automation dashboard built with Flask. It aggregates real-time data from Redis, MySQL, and MQTT and renders a single-page dashboard with jQuery-driven auto-refresh intervals.

## Commands

**Run locally (development):**
```bash
flask --app app --debug run --port 5002
```

**Deploy to production:**
```bash
./deploy.sh
```
This copies files to `/var/www/dashboard.spudooli.com/`, clears the Python cache, and restarts the systemd service `dashboard.spudooli.com.service`.

There are no tests or linting configured.

## Architecture

**Backend (`app.py`):** A single Flask file exposing 30+ JSON endpoints. Each endpoint reads from Redis, MySQL, a local JSON file, or makes outbound HTTP/socket requests, then returns JSON. There is no shared state between requests beyond the Redis and MySQL connections defined at module level.

**Frontend (`templates/index.html` + `static/`):** A single HTML page. jQuery polls each Flask endpoint on its own interval (ranging from 6 seconds for power draw to 12 hours for sunrise/sunset) and updates DOM elements in place. No build step — plain HTML/CSS/JS.

**Data sources:**
- **Redis** (`localhost:6379`) — real-time sensor readings written by external systems (temperatures, power draw, etc.)
- **MySQL** (`localhost`, db `spudooli`) — historical records for bank balance history, financial tracking
- **MQTT** (`192.168.1.2:1883`) — publishes financial totals to `house/money/` topics
- **External JSON** (`/var/www/scripts/spa-operations.json`) — spa/hot water cylinder operating status
- **config.py** — Google Maps API key (not committed values — keep this file out of version control as needed)

**Deployment:** Gunicorn runs the app at port 5002 under systemd. The `deploy.sh` script is a straight file copy — there is no CI/CD pipeline.
