from fastapi import FastAPI
from utils.thread_pool import main_loop
from uvicorn import Config, Server

from fastapi.middleware.cors import CORSMiddleware

from auth.auth_api import auth_api
from task_core.task_api import task_api

app = FastAPI(title="TaskStack", description="A simple task manager run on server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api)
app.include_router(task_api)


def main():
    config = Config(app, "0.0.0.0", 5555, loop=main_loop)
    server = Server(config=config)
    main_loop.run_until_complete(server.serve())


if __name__ == "__main__":
    main()
