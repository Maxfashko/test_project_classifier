import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


class Logger(object):
    """docstring for Logger"""

    def __init__(self, device_id, log_path, logger, log_name="Log.txt", log_level=logging.INFO):
        super(Logger, self).__init__()
        self.logger = logger
        self.device_id = device_id
        self.logger.propagate = False
        self.log_path = log_path
        self.log_name = log_name
        self.log_level = log_level

        if not Path(log_path).exists():
            Path(log_path).mkdir(parents=True, exist_ok=True)

        self.set_logger()

    def flush(self):
        pass

    def set_logger(self):
        self.logger.setLevel(self.log_level)

        rfh = RotatingFileHandler(
            os.path.join(self.log_path, self.log_name), mode="a", maxBytes=904857, backupCount=0,
        )
        self.logger.addHandler(rfh)

        # create the logging file handler
        fh = logging.FileHandler(os.path.join(self.log_path, self.log_name))
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - {device_id} - [%(filename)s:%(lineno)s - %(funcName)10s()] - %(message)s".format(
                device_id="device:" + str(self.device_id)
            )
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_path, device_id, log_name="Log.txt", log_level=logging.INFO):
        self.logger = logger
        self.logger.propagate = False
        self.log_level = log_level
        self.linebuf = ""
        self.log_path = log_path
        self.log_name = log_name
        self.device_id = device_id
        self.set_param = self.set_param()

        if not Path(log_path).exists():
            Path(log_path).mkdir(parents=True, exist_ok=True)

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

    def set_param(self):
        rfh = RotatingFileHandler(
            os.path.join(self.log_path, self.log_name), mode="a", maxBytes=904857, backupCount=0,
        )
        self.logger.addHandler(rfh)

        # create the logging file handler
        fh = logging.FileHandler(os.path.join(self.log_path, self.log_name))
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - {device_id} - [%(filename)s:%(lineno)s - %(funcName)10s()] - %(message)s".format(
                device_id="device:" + str(self.device_id)
            )
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
