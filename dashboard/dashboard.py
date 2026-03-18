#!/usr/bin/env python3
"""
Apex Exotics — Unified Dashboard Gateway

Proxies to:
  - sports-monitor (port 5001) — live games, channel switching, headlines
  - edgar-monitor  (port 5002) — portfolio, futures, scalping, news
  - march-madness  — bracket data via sports-monitor's /api/march_madness

Run: python dashboard.py
Open: http://localhost:5000
"""

from flask import Flask, render_template, request, Response
import requests

app = Flask(__name__)

BACKENDS = {
    "sports": "http://127.0.0.1:5001",
    "markets": "http://127.0.0.1:5002",
}


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/sports/<path:path>", methods=["GET", "POST", "DELETE"])
def proxy_sports(path):
    return _proxy(BACKENDS["sports"], path)


@app.route("/markets/<path:path>", methods=["GET", "POST", "DELETE"])
def proxy_markets(path):
    return _proxy(BACKENDS["markets"], path)


def _proxy(base, path):
    url = f"{base}/{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            params=request.args,
            json=request.get_json(silent=True) if request.is_json else None,
            data=request.data if not request.is_json else None,
            headers={"Content-Type": request.content_type or "application/json"},
            timeout=30,
        )
        return Response(resp.content, status=resp.status_code,
                        content_type=resp.headers.get("Content-Type", "application/json"))
    except requests.ConnectionError:
        return {"error": f"Backend unavailable: {base}"}, 502


if __name__ == "__main__":
    print("=" * 60)
    print("APEX EXOTICS — Unified Dashboard")
    print("=" * 60)
    print()
    print("  Gateway:  http://localhost:5000")
    print("  Sports:   http://localhost:5001  (sports-monitor)")
    print("  Markets:  http://localhost:5002  (edgar-monitor)")
    print()
    app.run(host="0.0.0.0", port=5000, debug=False)
