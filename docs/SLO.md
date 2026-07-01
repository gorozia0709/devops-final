# Service Level Objectives

## Service

`flask-app` - Flask application exposing `/`, `/health`, `/metrics`, and `/error`.

---

## Objectives

| SLI | SLO | How measured |
|---|---|---|
| Availability | 99% of requests return non-5xx over any 5-minute window | `app_requests_total` vs `app_errors_total` counters |
| Error rate | Fewer than 5 errors per minute under normal load | `rate(app_errors_total[1m]) * 60` |

---

## Error budget

- 99% availability over 5 minutes = max 3 seconds of errors per 5-minute window allowed.
- When `HighErrorRate` fires, the error budget is being consumed. Stop new deploys and investigate immediately.

---

## How it is measured

- **Prometheus** scrapes `app:5000/metrics` every 15 seconds.
- `app_requests_total` counts every request labeled by method, path and status.
- `app_errors_total` counts every 500 response.
- The `HighErrorRate` alert (`rate(app_errors_total[1m]) * 60 > 5`) serves as the SLO burn signal.
- The `AppDown` alert (`up{job="flask-app"} == 0`) signals total availability loss.

---

## Alerts

| Alert | Expression | Meaning                           |
|---|---|-----------------------------------|
| `HighErrorRate` | `rate(app_errors_total[1m]) * 60 > 5` | SLO at risk - error rate too high |
| `AppDown` | `up{job="flask-app"} == 0` for 1m | Total availability loss           |

---

## Incident response

If an SLO alert fires, follow the steps in [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md).