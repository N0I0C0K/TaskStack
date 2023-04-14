import time


def formate_time(time_seco: float):
    return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time_seco))
