import logging

def setup_logger():
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.FileHandler('linkedin_scraper.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        logger.setLevel(logging.DEBUG)
    
    return logger