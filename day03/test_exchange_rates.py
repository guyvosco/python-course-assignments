#!/usr/bin/env python

'''
pytest test suite for the exchange_rates function in utilities module.
The rates dictionary is hardcoded for testing purposes to allow consistent results.
'''

import pytest
from utilities import exchange_rates

@pytest.mark.parametrize("amount, from_currency, to_currency, expected", [
    (1.0,   'ILS', 'ILS', 1.000000),
    (1.0,   'USD', 'ILS', 3.230000),
    (1.0,   'EUR', 'ILS', 3.738425),
    (1.0,   'GBP', 'ILS', 4.255599),
    (100.0, 'JPY', 'ILS', 2.097402),
    (1.0,   'CHF', 'ILS', 4.012422),
    (1.0,   'AUD', 'ILS', 2.111111),
    (1.0,   'CAD', 'ILS', 2.307142),
    (1.0,   'SEK', 'ILS', 0.340000),
    (1.0,   'NOK', 'ILS', 0.319802),
    (1.0,   'DKK', 'ILS', 0.500775),
])
def test_parametrized(amount, from_currency, to_currency, expected):
    rates = {'ILS': 3.23, 'USD': 1.0, 'EUR': 0.864, 'GBP': 0.759, 'JPY': 154., 'CHF': 0.805, 'AUD': 1.53, 'CAD': 1.40, 'SEK': 9.50, 'NOK': 10.1, 'DKK': 6.45}
    assert exchange_rates(rates, amount, from_currency, to_currency) == pytest.approx(expected)

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
