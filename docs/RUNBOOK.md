# Incident Response Runbook

This document describes what to do when something goes wrong with the application.
Follow the steps in order. Each section covers one type of problem.

---

## How to know something is wrong

Open Prometheus alerts page: http://localhost:9090/alerts

You will see one of two alerts firing:
- **HighErrorRate** - the app is responding but returning too many errors
- **AppDown** - the app is completely unreachable

---

## Alert 1: HighErrorRate

**What it means:**
The app has returned more than 5 errors (HTTP 500) per minute.
The app is still running but something is causing it to fail on requests.

**Step 1 - Confirm the alert is real**
Open http://localhost:9090/alerts and confirm `HighErrorRate` shows as FIRING.

**Step 2  Find out which requests are failing**
Open Grafana at http://localhost:3000, go to Explore, select Loki as the data source and run this query:
```
{container="app"} |= "500"
```

This shows you every failed request with its timestamp and path.
Look for a pattern - is it one specific endpoint failing? Is it happening constantly or in bursts?

**Step 3 - Check if the container is healthy**
Run this in your terminal:
```
docker compose ps
docker compose logs app --tail=50
```
Confirm the app container is running and check logs for any Python errors or exceptions.

**Step 4 - Fix it**

If the errors started after a recent code push (bad deploy):
```
ansible-playbook -i ansible/inventory.ini ansible/rollback.yml --ask-become-pass
```
This reverts the app to the previous working version.

If the container is crashing or in a restart loop:
```
docker compose restart app
```

**Step 5 - Confirm recovery**
```
curl http://localhost:5000/health
```
Should return `{"status": "ok"}`.

Wait 1-2 minutes and check http://localhost:9090/alerts and the `HighErrorRate` alert should disappear (go from FIRING to inactive).

---

## Alert 2: AppDown

**What it means:**
Prometheus cannot reach the app at all. The app container is likely stopped or crashed.

**Step 1 - Confirm the alert is real**
Open http://localhost:9090/alerts and confirm `AppDown` shows as FIRING.
Also check http://localhost:9090/targets, the `flask-app` target should show as DOWN.

**Step 2 - Check container status**
```
docker compose ps
```
Look at the `app` container — is it `running`, `exited`, or `restarting`?

**Step 3 - Check what caused it to stop**
```
docker compose logs app --tail=100
```
Look for any error messages, out of memory errors, or Python exceptions.

**Step 4 - Fix it**

If the container simply stopped:
```
docker compose start app
```

If the container keeps crashing immediately after starting:
```
docker compose restart app
```

If the problem started after a deploy and keeps happening:
```
ansible-playbook -i ansible/inventory.ini ansible/rollback.yml --ask-become-pass
```

**Step 5 - Confirm recovery**
```
curl http://localhost:5000/health
```
Should return `{"status": "ok"}`.

Check http://localhost:9090/targets - `flask-app` should show as UP again.
The `AppDown` alert will clear automatically within about 1 minute.

---

## Rollback procedure 

Use this any time you want to revert to the previous deployment regardless of alerts:

```
# See which slot is currently active
cat ansible/active_slot.yml

# Run rollback — switches to the other slot automatically
ansible-playbook -i ansible/inventory.ini ansible/rollback.yml --ask-become-pass
```

The rollback playbook:
1. Starts the previous slot
2. Health checks it before switching
3. Updates `active_slot.yml` to point to the recovered slot
4. Stops the broken slot

If the rollback itself fails (previous slot also unhealthy), restart the full stack:
```
docker compose down
docker compose up -d --build
```

---

## Service Level Objective (SLO)

**Definition:** 99% of all HTTP requests over any 5-minute window must return a non-5xx response.

**How it is measured:** Using the `app_requests_total` and `app_errors_total` Prometheus counters that the app exposes at `/metrics`.

**What triggers action:** The `HighErrorRate` alert fires when errors exceed 5 per minute, which indicates the SLO is at risk of being breached. Follow the HighErrorRate steps above immediately.

---

## Quick reference

| Problem | First command to run |
|---|---|
| App returning errors | `docker compose logs app --tail=50` |
| App completely down | `docker compose start app` |
| Bad deploy, need to revert | `ansible-playbook -i ansible/inventory.ini ansible/rollback.yml --ask-become-pass` |
| Full restart from scratch | `docker compose down && docker compose up -d --build` |
| Check all containers | `docker compose ps` |