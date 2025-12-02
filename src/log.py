import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("mylogger")
logger.setLevel(logging.INFO)

# log file setup
file_handler = TimedRotatingFileHandler(
    filename="/opt/app.log",
    when="midnight",   
    interval=1,
    backupCount=7,
    encoding="utf-8"
)

file_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)

# -------------------------------------------------------------------
# terminal output set
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_formatter = logging.Formatter(
    "%(message)s"
)
console_handler.setFormatter(console_formatter)


# -------------------------------------------------------------------
logger.addHandler(file_handler)
logger.addHandler(console_handler)


