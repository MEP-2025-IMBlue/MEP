from fastapi import FastAPI
from src.api.routes.KIImage_routes import router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome"}


app.include_router(router)
