from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from todo_app.api import router
from todo_app.handlers.server_exception_handler import handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# 引数；反応してほしいもの, 反応した際の処理
app.add_exception_handler(Exception, handler)
