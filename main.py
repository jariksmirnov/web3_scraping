from apscheduler.schedulers.blocking import BlockingScheduler
import os
import time

from web3 import main as main_web3
from cryptocurrencyjobs import main as main_crypto
from linkedin import main as main_linkedin
from remote3 import main as main_remote3
from cryptojobslist import main as main_cryptojob
from myweb3 import main as main_myweb3


# list of info folders to create
folders = ['web3.career', 'cryptocurrencyjobs', 'linkedin', 'remote3', 'cryptojob', 'myweb3', ]
pause = 1 * 60  # pause between changing sites
period = 60 * 60  # 1hrs period to scrap new items

for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"created {folder}")
    else:
        print(f"{folder} already exists")

# run scheduled task for different sites
# scheduler = BlockingScheduler()
# scheduler.add_job(main_web3, 'interval', minutes=2)
# scheduler.add_job(main_crypto, 'interval', minutes=2)
# scheduler.add_job(main_linkedin, 'interval', minutes=2)
# scheduler.add_job(main_remote3, 'interval', minutes=2)
# scheduler.add_job(main_cryptojob, 'interval', minutes=2)
# scheduler.add_job(main_myweb3, 'interval', minutes=2)
# scheduler.start()


def run_initial_tasks():
    print('starting web3.career')
    main_web3()
    time.sleep(pause)
    print('starting cryptocurrencyjobs')
    main_crypto()
    time.sleep(pause)
    print('starting linkedin')
    main_linkedin()
    time.sleep(pause)
    print('starting remote3')
    main_remote3()
    time.sleep(pause)
    print('starting cryptojob')
    main_cryptojob()
    time.sleep(pause)
    print('starting myweb3')
    main_myweb3()



def run_periodically():
    while True:
        run_initial_tasks()
        print("running all tasks periodically")
        time.sleep(period)


if __name__ == "__main__":
    run_initial_tasks()
    run_periodically()
