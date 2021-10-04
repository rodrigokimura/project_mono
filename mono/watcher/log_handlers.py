import logging


class WatcherHandler(logging.Handler):
    """An exception log handler that stores log entries to database.
    If the request is passed as the first argument to the log record, 
    request data will be provided in the email report. 
    """
    
    def emit(self, record):
        try:
            request = record.request
        except Exception:
            request = None