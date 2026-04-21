from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .games import router as items_router

routes = FastAPI()

routes.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routes.include_router(items_router)