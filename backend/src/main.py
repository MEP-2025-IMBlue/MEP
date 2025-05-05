from fastapi import FastAPI
#from src.api.routes.KIImage_routes import router
from src.api.routes import KIContainer_routes,KIImage_routes 

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome"}


app.include_router(KIImage_routes.router)
app.include_router(KIContainer_routes.router)