import logging, os
#from utils.webhook import sendWebhook

logging.basicConfig(level=logging.INFO, filename="logs.txt", format='%(asctime)s|%(name)s|%(levelname)s|%(message)s',datefmt='%d-%b-%y %I:%M:%S %p')

def print_message(text, alert_type):
    logging.info(text)
    #sendWebhook(alert_type,text)
