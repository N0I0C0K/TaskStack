from utils.scheduler import scheduler, CronTrigger
import time


def test_scheduler():
    scheduler.start()
    t = 0

    def crontab_exp_func():
        nonlocal t
        t += 1
        print("scheduler invoke")

    scheduler.add_job(
        crontab_exp_func,
        trigger=CronTrigger.from_crontab("* * * * *"),
    )
    _n = 0
    while t == 0 and _n < 70:
        time.sleep(1)
        _n += 1
    assert t > 0


def test_scheduler_pause():
    scheduler.start()
    t = 0

    def crontab_exp_func():
        nonlocal t
        t += 1
        print("scheduler invoke")

    job = scheduler.add_job(
        crontab_exp_func,
        trigger=CronTrigger.from_crontab("* * * * *"),
    )
    job.pause()
    _n = 0
    while t == 0 and _n < 70:
        time.sleep(1)
        _n += 1
    assert t == 0


def test_scheduler_resume():
    scheduler.start()
    t = 0

    def crontab_exp_func():
        nonlocal t
        t += 1
        print("scheduler invoke")

    job = scheduler.add_job(
        crontab_exp_func,
        trigger=CronTrigger.from_crontab("* * * * *"),
    )
    job.pause()
    job.resume()
    _n = 0
    while t == 0 and _n < 70:
        time.sleep(1)
        _n += 1
    assert t > 0
