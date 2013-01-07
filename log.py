import logging

def create_logger(name):
    """
    create a new stream logger setup at INFO level
    """


    log = logging.getLogger(name)
    del log.handlers[:]
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)-5s %(name)-5s %(pathname)s:%(lineno)s - %(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    return log

