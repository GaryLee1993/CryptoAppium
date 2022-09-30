# -*- coding: utf-8 -*-
# ProjectName: SenseSpring-QA
# DateTime: 2020/1/2 10:31

__author__ = "Xiao Bin"
import os
import time
import logging
from logging.handlers import RotatingFileHandler


LOG_LEVEL = {
    "warning": logging.WARNING,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def get_current_log(path=None, file_prefix="test", c_level="info", f_level="info"):
    c_level, f_level = c_level.lower(), f_level.lower()
    assert c_level in LOG_LEVEL and f_level in LOG_LEVEL, f"Params Error, expected [waring, debug, info, error, " \
        f"critical]"
    path = path or log_path()
    return log_config(c_level=LOG_LEVEL[c_level], f_level=LOG_LEVEL[f_level], out_path=path, filename=file_prefix)[0]


def log_path():
    """Get log directory"""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log")
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def log_config(f_level=logging.INFO, c_level=logging.CRITICAL, out_path='', filename='info', fix=False):
    logfile = os.path.join(out_path, filename) + '-' + time.strftime('%Y_%m%d_%H%M%S', time.localtime()) + '.log' \
        if not fix else os.path.join(out_path, filename) + '.log'
    logger = logging.getLogger(logfile)

    if f_level is None:
        if c_level is None:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(c_level)
    else:
        logger.setLevel(f_level)

    formatter = logging.Formatter(
        '[%(levelname)s][%(process)d][%(thread)d]--%(asctime)s--[%(filename)s %(funcName)s %(lineno)d]: %(message)s')

    if c_level is not None:
        ch = logging.StreamHandler()
        ch.setLevel(c_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if f_level is not None:
        fh = RotatingFileHandler(logfile, maxBytes=100 * 1024 * 1024, backupCount=100)
        fh.setLevel(f_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger, logfile


if __name__ == "__main__":
    print(log_path())
