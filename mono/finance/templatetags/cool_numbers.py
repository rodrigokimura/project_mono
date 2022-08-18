"""Custom template tags"""
from django import template

register = template.Library()


@register.filter(name="cool_numbers", is_safe=False)
def cool_numbers(val, precision=2):
    """
    Format using K, M
    """
    try:
        int_val = int(val)
    except ValueError as value_error:
        raise template.TemplateSyntaxError(
            f"Value must be an integer. {val} is not an integer"
        ) from value_error
    if int_val < 1_000:
        return str(int_val)
    if int_val < 1_000_000:
        return f"{ int_val/1_000:.{precision}f}".rstrip("0").rstrip(".") + "K"
    return f"{int_val/1_000_000:.{precision}f}".rstrip("0").rstrip(".") + "M"


@register.filter(is_safe=False)
def stripe_currency(val, currency):
    """
    Format based on currency
    """
    try:
        int_val = int(val)
    except ValueError as value_error:
        raise template.TemplateSyntaxError(
            f'Value must be an integer. "{val}" is not an integer'
        ) from value_error

    if currency == "brl":
        decimal_places = 2
    elif currency == "usd":
        decimal_places = 2
    else:
        raise template.TemplateSyntaxError(
            f"Non recognized currency code: {currency}."
        )

    return int_val / (decimal_places * 10)
