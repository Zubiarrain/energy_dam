import logging as log

logger = log.basicConfig(
    level = log.INFO,
    format = '%(asctime)s: %(levelname)s [%(message)s]',
    datefmt = '%d/%m/%Y %I:%M:%S %p',
    handlers = [
        log.FileHandler('logs/ENERGÍA-Consigna_Déficit.log',encoding='utf-8'),
        log.StreamHandler()
    ],
    encoding='utf-8'
)


# Create a custom self.logger
logger = log.getLogger(logger)