import functools
import logging
import time

logger = logging.getLogger(__package__)


def retry(exception_to_check=Exception, tries: int = 3, delay: int = 1):
    def _retry(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            attempts = tries
            while attempts > 1:
                try:
                    return method(*args, **kwargs)
                except exception_to_check as error:
                    attempts -= 1
                    logger.warning(
                        f"Error occured on {method.__name__}.\n"
                        + f"Error message: {error}\n"
                        + f"Retrying in {delay} seconds. Attempts left: {attempts}\n"
                    )
                    time.sleep(delay)
            return method(*args, **kwargs)

        return wrapper

    return _retry
