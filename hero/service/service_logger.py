import logging

log = logging.getLogger("hero:service")

def log_errors(func):
    def wrapper(*args, **kwargs):
        try:
            # print('Hi, im about to do the function, woop woop')
            res = func(*args, **kwargs)
            # print('Function complete, woop woop')
            return res
        except:
            log.error('Hero Service Error: \n', exc_info=True)
    return wrapper
