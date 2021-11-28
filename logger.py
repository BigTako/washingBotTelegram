import logging

handler = logging.FileHandler('logs.log', 'a', 'utf-8')
logging.basicConfig(level="INFO", format="%(filename)s-%(module)s-"
                                         "%(levelname)s -"
                                         "%(funcName)s - %(message)s - %(asctime)s\n")

logger = logging.getLogger()
logger.addHandler(handler)

def log_func(func):
    """Функция для логирования(не предназначена для ф-ий машины состояний)"""
    def wrapper(*args):
        logger.info(f"User called {func.__name__}")
        try:
            return func(*args)
        except Exception as ex:
            logger.error(f"Function: {func.__name__}.\nArguments: {args}\nError: {ex}")
            return -1
    return wrapper


