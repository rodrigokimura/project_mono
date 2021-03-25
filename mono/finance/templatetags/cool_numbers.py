from django import template

register = template.Library()

@register.filter(name='cool_numbers', is_safe=False)
def cool_numbers(val, precision=2):
    try:
      int_val = int(val)
    except ValueError:
        raise template.TemplateSyntaxError(
            f'Value must be an integer. {val} is not an integer')
    if int_val < 1000:
        return str(int_val)
    elif int_val < 1_000_000:
        return f'{ int_val/1000.0:.{precision}f}'.rstrip('0').rstrip('.') + 'K'
    else:
        return f'{int_val/1_000_000.0:.{precision}f}'.rstrip('0').rstrip('.') + 'M'

@register.filter(is_safe=False)
def stripe_currency(val, currency):
    try:
        int_val = int(val)
    except ValueError:
        raise template.TemplateSyntaxError(
            f'Value must be an integer. {val} is not an integer')

    if currency == 'brl':
        decimal_places = 2
    elif currency == 'usd':
        decimal_places = 2
    else:
        raise template.TemplateSyntaxError(f'Non recognized currency code: {currency}.')

    return int_val/(decimal_places*10)