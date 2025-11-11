# day03 - Assignment

I wrote a Python app that prints and converts travel expenses to your currency, helping you track your budget.
All code was written manually.

---

## travel_expenses.py
**No installs needed.**

The code uses a free and open-access API (https://www.exchangerate-api.com/docs/free) to get the current (updated once per day) `rates`. 
The **business logic** is implemented in the `exchange_rates` function (from the `utilities` module), which converts a given `amount` from `from_currency` to `to_currency` (`ILS` by default) using a provided `rates` dictionary.

You can run the code in two ways:

- By passing system arguments in triplets:
  
  `python travel_expences.py title1 amount1 currency1 title2 amount2 currency2 ...`

  Example: `python travel_expences.py Texi 160 ILS Flight 4000 USD Lunch 22.5 CHF`

- If no arguments are provided, it prompts you interactively to enter the triplets `title amount currency` one by one (type `done` to finish).  

### test_exchange_rates.py
Dependencies: 
- [`pytest`](https://pypi.org/project/pytest/) (install using: `uv add pytest` or `pip install pytest`)

This code provides a test suite for the `exchange_rates` function. The rates dictionary is hardcoded for testing purposes, ensuring consistent and reproducible test results.

Run using:

`pytest test_exchange_rates.py`

or

`pytest -v test_exchange_rates.py`

## travel_expenses_ext_lib.py
Dependencies: 
- [`currencyconverter`](https://pypi.org/project/CurrencyConverter/) (install using: `uv add currencyconverter` or `pip install currencyconverter`)
  
This code uses an alternative **business logic** implementation that relies on a *3rd-party library* for the conversions. 

> [!NOTE]
> The two implementations use different data sources, updated at different frequencies, so small discrepancies are expected between the results.
