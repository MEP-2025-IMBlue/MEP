from fastapi import FastAPI
from backend.src.api.routes.KIImage_routes import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome"}


app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5501"],  # oder ["*"] für alles
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)