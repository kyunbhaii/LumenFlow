from fastapi import FastAPI

app = FastAPI(
    title="LumenFlow"
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
