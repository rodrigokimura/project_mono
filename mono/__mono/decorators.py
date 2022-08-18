"""Useful decorators"""
import logging
import warnings

import stripe

logger = logging.getLogger(__name__)


def stripe_exception_handler(func):
    """Gracefully handle Stripe exceptions"""

    def wrapper(
        *args, **kwargs
    ):  # pylint: disable=inconsistent-return-statements
        try:
            return func(*args, **kwargs)
        except stripe.error.CardError as card_error:
            logger.warning("Status is: %s", card_error.http_status)
            logger.warning("Code is: %s", card_error.code)
            logger.warning("Param is: %s", card_error.param)
            logger.warning("Message is: %s", card_error.user_message)
        except stripe.error.RateLimitError:
            logger.warning("Too many requests made to the API too quickly")
        except stripe.error.InvalidRequestError:
            logger.warning("Invalid parameters were supplied to Stripe's API")
        except stripe.error.AuthenticationError:
            logger.logging.warning("Authentication with Stripe's API failed")
        except stripe.error.APIConnectionError:
            logger.warning("Network communication with Stripe failed")
        except stripe.error.StripeError:
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
