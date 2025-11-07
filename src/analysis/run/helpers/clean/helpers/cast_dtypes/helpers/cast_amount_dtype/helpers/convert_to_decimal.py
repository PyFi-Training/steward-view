from decimal import Decimal

def convert_to_decimal(value):
    cent = Decimal('0.01')
    return Decimal(value).quantize(cent)