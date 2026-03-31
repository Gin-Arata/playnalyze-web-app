from fastapi import FastAPI

routes = FastAPI()

@routes.get("/hello-world")
def read_root():
    return {"message": "Hello World!"}