"""Useful decorators"""
import logging
import warnings

from stripe.error import (
    APIConnectionError,
    AuthenticationError,
    CardError,
    InvalidRequestError,
    RateLimitError,
    StripeError,
)

logger = logging.getLogger(__name__)


def stripe_exception_handler(func):
    """Gracefully handle Stripe exceptions"""

    def wrapper(  # pylint: disable=inconsistent-return-statements
        *args, **kwargs
    ):
        try:
            return func(*args, **kwargs)
        except CardError as card_error:
            logger.warning("Status is: %s", card_error.http_status)
            logger.warning("Code is: %s", card_error.code)
            logger.warning("Param is: %s", card_error.param)
            logger.warning("Message is: %s", card_error.user_message)
        except RateLimitError:
            logger.warning("Too many requests made to the API too quickly")
        except InvalidRequestError:
            logger.warning("Invalid parameters were supplied to Stripe's API")
        except AuthenticationError:
            logger.warning("Authentication with Stripe's API failed")
        except APIConnectionError:
            logger.warning("Network communication with Stripe failed")
        except StripeError:
            logger.warning("Stripe generic error")

    return wrapper


def ignore_warnings(test_func):
    """Ignore warnings, useful when running tests"""

    def do_test(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            logging.disable(logging.CRITICAL)
            test_func(*args, **kwargs)

    return do_test
