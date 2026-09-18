from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.routing import Match

app = FastAPI(
    title="DevOps CI/CD API",
    version="1.0.0",
)

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ("method", "path", "status_code"),
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "path"),
)


@app.middleware("http")
async def record_http_metrics(request: Request, call_next) -> Response:
    if request.url.path == "/metrics":
        return await call_next(request)

    started_at = perf_counter()
    response = await call_next(request)
    path = "unknown"
    for route in app.router.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            path = getattr(route, "path", "unknown")
            break
    duration = perf_counter() - started_at

    http_requests_total.labels(request.method, path, str(response.status_code)).inc()
    http_request_duration_seconds.labels(request.method, path).observe(duration)
    return response


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FastAPI CI/CD project is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/version")
def get_version() -> dict[str, str]:
    return {"version": app.version}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
