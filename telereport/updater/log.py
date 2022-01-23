class Logger:
    import logging
    from logging.handlers import RotatingFileHandler

    def __init__(self, name, to_file=True, to_stdout=True, path=None, string_format=None, level=logging.DEBUG):
        self.logger = self.logging.getLogger(name)
        self._handlers = list()

        if to_file:
            self._handlers.append(
                self.RotatingFileHandler(
                    filename=path or '/var/log/tele-report.log',
                    maxBytes=5 << 20,
                    backupCount=3
                )
            )

        if to_stdout:
            self._handlers.append(self.logging.StreamHandler())

        self._formatter = self.logging.Formatter(string_format or '%(levelname)-7s [%(asctime)s] [%(name)-5s] %(message)s')

        self.logger.setLevel(level)

        for handler in self._handlers:
            handler.setFormatter(self._formatter)
            self.logger.addHandler(handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)
