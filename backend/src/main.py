from fastapi import FastAPI
from api.routes import images, containers

app = FastAPI()

app.include_router(containers.router)
app.include_router(images.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}