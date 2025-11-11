def exchange_rates(rates, amount, from_currency, to_currency):
    try:
        amount = float(amount)
    except ValueError:
        raise ValueError('Amount must be a number.')
    
    if from_currency not in rates or to_currency not in rates:
        raise ValueError('Unsupported currency code.\nSupported codes are: ' + ', '.join(rates.keys()))

    return amount * rates[to_currency] / rates[from_currency]