import time
import logging
import json
import os
from flask import Flask, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

SLOT = os.environ.get("SLOT", "unknown")
PORT = int(os.environ.get("PORT", 5000))

REQUEST_COUNTER = Counter(
    'app_requests_total',
    'Total number of requests',
    ['method', 'path', 'status']
)

ERROR_COUNTER = Counter('app_errors_total', 'Total number of errors')


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage()
        })


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


@app.after_request
def log_request(response):
    log_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "level": "INFO",
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "duration_ms": 0
    }

    logger.info(json.dumps(log_data))

    REQUEST_COUNTER.labels(
        method=request.method,
        path=request.path,
        status=response.status_code
    ).inc()

    return response


@app.route("/")
def index():
    return {"message": "ok", "slot": SLOT}, 200


@app.route("/error")
def error():
    ERROR_COUNTER.inc()
    return {"message": "forced error"}, 500


@app.route("/health")
def health():
    return {"status": "ok", "slot": SLOT}, 200


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
