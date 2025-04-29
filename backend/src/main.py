from fastapi import FastAPI
from backend.src.api.routes.KIImage_routes import router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(router)
