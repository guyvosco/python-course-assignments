# day04 - Assignment

I wrote a Python app that prints and converts travel expenses to your currency, helping you track your budget.
The code was originally written for assignment day02 with ChatGPT-5 and then modified manually for this assignment.

## travel_expenses_gui.py
**No installs needed.**

The code uses a free and open-access API ((ExchangeRate API)[https://www.exchangerate-api.com/docs/free]) to get the current (updated once per day) exchange rates. It downloads and reads the data from `rates_cache.json`. If the file does not exist, or if the user wants to refresh the data (using the `Reload rates` button), the program fetches the latest rates from the API.
The **business logic** is implemented in the `utilities` module:
- `get_currency_rates` - reads the cached data file or retrieves new data from the API when needed.
- `exchange_rates`: converts a given `amount` from `Currency` to `your_currency` using a provided `rates` dictionary.
