"""Configure handlers and formats for application loggers."""
import logging
import sys

from loguru import logger

from app.utils.settings import Settings


class InterceptHandler(logging.Handler):
    """ Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_exception(record: dict) -> str:
    """Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    """
    format_string = '{{"date":"{time:YYYY-MM-DDTHH:mm:ss[Z]}",' \
                    '"level":"{level}",' \
                    '"name":"{name}.{function}",' \
                    '"message":"{message}",' \
                    '"exception":"{exception}"'

    if "content_key" in record["extra"]:
        format_string += ',"content_key":"{extra[content_key]}"'

    format_string += "}}\n"

    return format_string


def init_logging(config: Settings):
    """Replaces logging handlers with a handler for using the custom handler.
    WARNING!
    if you call the init_logging in startup event function,
    then the first logs before the application start will be in the old format
    """
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
    )

    # change handler for everyone
    intercept_handler = InterceptHandler()
    for every_logger in loggers:
        every_logger.handlers = []
        every_logger.handlers = [intercept_handler]

    # set logs output, level and format
    log_handlers = [{"sink": config.info_log, "level": logging.INFO, "format": format_exception},
                    {"sink": config.warn_log, "level": logging.WARNING, "format": format_exception},
                    {"sink": config.error_log, "level": logging.ERROR, "format": format_exception}]
    if config.isdebug:
        log_handlers.append({"sink": sys.stdout, "level": logging.DEBUG, "format": format_exception})

    logger.configure(handlers=log_handlers)
