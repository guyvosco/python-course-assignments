import os
import json
import urllib.request

def exchange_rates(rates, amount, from_currency, to_currency):
    try:
        amount = float(amount)
    except ValueError:
        raise ValueError('Amount must be a number.')
    
    if from_currency not in rates or to_currency not in rates:
        raise ValueError('Unsupported currency code.\nSupported codes are: ' + ', '.join(rates.keys()))

    return amount * rates[to_currency] / rates[from_currency]

def get_currency_rates(refresh = False):
    if os.path.exists('rates_cache.json') and not refresh:
        with open('rates_cache.json', 'r') as f:
            return json.load(f)
    else:
        api_url = 'https://open.er-api.com/v6/latest/USD'
        data = json.loads(urllib.request.urlopen(api_url).read())
        with open('rates_cache.json', 'w') as f:
            json.dump(data, f)
            
    return data