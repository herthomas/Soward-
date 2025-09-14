from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from api.routes import transcript,generate

app = FastAPI(title="Soward API", version="1.0.0")

@app.get("/")
async def root():
    return RedirectResponse(url="https://soward.app/")

app.include_router(transcript.router)
app.include_router(generate.router)