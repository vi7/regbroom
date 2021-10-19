import datetime


def set_config(conf):
    global config
    config = conf

def log(msg):
    """Print the message with timestamp
    """
    curr_time = datetime.datetime.now()
    print("{}: {}".format(curr_time, msg))

def log_debug(msg):
    """Pring the message with timestamp
    if debug mode enabled in the config
    """
    if not config['debug']:
        return
    curr_time = datetime.datetime.now()
    print("{}: [DEBUG] {}".format(curr_time, msg))
