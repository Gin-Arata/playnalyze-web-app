from fastapi import FastAPI
from .games import router as items_router

routes = FastAPI()

@routes.get("/hello-world")
def read_root():
    return {"message": "Hello World!"}

routes.include_router(items_router)