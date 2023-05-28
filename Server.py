from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from auth.auth_api import auth_api
from task_core.task_api import task_api
from utils.scheduler import scheduler
from utils.thread_pool import main_loop

from user.user_center import user_center
from user.user_api import user_api

user_center.init()

app = FastAPI(title="TaskStack", description="A simple task manager run on server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_api)
api_router.include_router(task_api)
api_router.include_router(user_api)

app.include_router(api_router)


def main():
    config = Config(app, "0.0.0.0", 5555, loop=main_loop)
    server = Server(config=config)
    scheduler.start()
    main_loop.run_until_complete(server.serve())


if __name__ == "__main__":
    main()
