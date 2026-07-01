# Incident Response

This document describes what to do when something goes wrong with the application.
Follow the steps in order.

---

## How to detect an incident

Open Prometheus alerts page: http://localhost:9090/alerts

Two alerts are configured:
- **HighErrorRate** - app is running but returning too many 500 errors
- **AppDown** - app is completely unreachable

---

## Alert: HighErrorRate

**What it means:** More than 5 errors per minute are being returned.
The app is still running but something is causing requests to fail.

**Step 1 - Confirm**
Check http://localhost:9090/alerts - confirm `HighErrorRate` shows as FIRING.

**Step 2 - Find the failing requests**
Open Grafana at http://localhost:3000 → Explore → Loki → run:
{container="app"} |= "500"

Look for a pattern - is one endpoint failing consistently?

**Step 3 - Check the container**
``` 
docker compose ps
docker compose logs app --tail=50
```

**Step 4 - Fix it**

If caused by a bad deploy:
``` 
ansible-playbook -i ansible/inventory.ini ansible/rollback.yml
```

If the container is crashing:
``` 
docker compose restart app
```

**Step 5 - Verify recovery**
``` 
curl http://localhost:5000/health
```
Should return `{"status": "ok"}`. Alert clears automatically within 1-2 minutes.

---

## Alert: AppDown

**What it means:** Prometheus cannot reach the app at all.
The container is likely stopped or crashed.

**Step 1 - Confirm**
Check http://localhost:9090/alerts - confirm `AppDown` shows as FIRING.
Check http://localhost:9090/targets - `flask-app` should show as DOWN.

**Step 2 - Check container status**
``` 
docker compose ps
docker compose logs app --tail=100
```

**Step 3 - Fix it**

If the container stopped:
``` 
docker compose start app
```

If it keeps crashing after a recent deploy:
``` 
ansible-playbook -i ansible/inventory.ini ansible/rollback.yml
```

**Step 4 - Verify recovery**
``` 
curl http://localhost:5000/health
```
Check http://localhost:9090/targets - `flask-app` should show as UP.
Alert clears automatically within 1 minute.

---

## Rollback procedure

``` 
# Check which slot is active
cat ansible/active_slot.yml

# Switch to previous slot
ansible-playbook -i ansible/inventory.ini ansible/rollback.yml
```

The rollback playbook:
1. Starts the previous slot
2. Health checks it before switching
3. Updates `active_slot.yml`
4. Stops the broken slot

If rollback also fails, restart the full stack:
``` 
docker compose down && docker compose up -d --build
```

---

## Quick reference

| Problem | First command |
|---|---|
| App returning errors | `docker compose logs app --tail=50` |
| App completely down | `docker compose start app` |
| Bad deploy | `ansible-playbook -i ansible/inventory.ini ansible/rollback.yml` |
| Full restart | `docker compose down && docker compose up -d --build` |
| Check all containers | `docker compose ps` |