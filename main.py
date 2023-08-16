from apscheduler.schedulers.blocking import BlockingScheduler
import os

from web3 import main as main_web3
from cryptocurrencyjobs import main as main_crypto
from linkedin import main as main_linkedin
from remote3 import main as main_remote3


# List of folder names you want to create
folders = ['web3.career', 'cryptocurrencyjobs', 'linkedin', 'remote3', 'cryptojob', 'myweb3',]


for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created {folder}")
    else:
        print(f"{folder} already exists")

# run scheduled task for different sites
scheduler = BlockingScheduler()
scheduler.add_job(main_web3, 'interval', minutes=2)
scheduler.add_job(main_crypto, 'interval', minutes=2)
scheduler.add_job(main_linkedin, 'interval', minutes=2)
scheduler.start()
