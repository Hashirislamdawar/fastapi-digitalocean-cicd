from fastapi import FastAPI

app = FastAPI(
    title="DevOps CI/CD API",
    version="1.0.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FastAPI CI/CD project is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/version")
def get_version() -> dict[str, str]:
    return {"version": app.version}
