import logging
import time
import os

log_file_name = time.strftime("%Y-%m-%d.log", time.localtime())

if not os.path.exists("./log"):
    print("create log dir")
    os.makedirs("./log")

# format='%(asctime)s- %(levelname)s- "%(pathname)s:%(lineno)d":\n%(message)s'

logging.basicConfig(
    filename=f"./log/{log_file_name}",
    filemode="a+",
    encoding="utf-8",
    format="%(asctime)s- %(levelname)s -> \n%(message)s",
    datefmt="%Y-%m-%d-%H:%M",
)
logger = logging.getLogger("mylogger")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

__all__ = ["logger"]
