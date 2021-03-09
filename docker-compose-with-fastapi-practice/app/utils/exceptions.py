from app.utils.logger import logger


class Exceptions:
    class UnprocessableEntity(Exception):
        def __init__(self, detail):
            logger.bind(exception=detail).error(self)

    class UnsupportedDocumentException(Exception):
        def __init__(self, detail):
            logger.bind(exception=detail).warning(self)

    class ClientException(Exception):
        def __init__(self, detail):
            logger.bind(exception=detail).error(self)

    class UnexpectedException(Exception):
        def __init__(self, detail):
            logger.bind(exception=detail).exception(self)
