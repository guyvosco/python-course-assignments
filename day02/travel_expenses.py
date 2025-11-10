#!/usr/bin/env python

'''
A script to calculate travel expenses in various currencies and convert them to ILS (Israeli Shekel).

Usage:
1. Command-line arguments:
   python travel_expences.py title1 amount1 currency1 title2 amount2 currency2 ...
2. Interactive input.
'''

import sys
import urllib.request
import json

def main():
    api_url = 'https://open.er-api.com/v6/latest/USD'
    your_currency = 'ILS'

    rates = json.loads(urllib.request.urlopen(api_url).read())['rates']

    argv = sys.argv
    if len(argv) > 1:
        expenses = []
        for title, amount, currency in zip(argv[1::3], argv[2::3], argv[3::3]):
            converted = exchange_rates(rates, amount, currency, your_currency)
            expenses.append((title, amount, currency, converted))

    else:
        expenses = []
        expense = input('Enter your expenses one by one in the format "Title Amount Currency" (e.g., "Lunch 12.5 USD").\n')
        while expense.lower() != "done":
            try:
                title, amount, currency = expense.split()
                converted = exchange_rates(amount, currency, your_currency, api_url)
                expenses.append((title, amount, currency, converted))
            
            except ValueError:
                print("Invalid input. Please enter the expense in the correct format.")
            expense = input('Add another expense or type "done" to finish.\n')
        
    print_expenses(expenses, your_currency)

def exchange_rates(rates, amount, from_currency, to_currency):
    try:
        amount = float(amount)
    except ValueError:
        raise ValueError('Amount must be a number.')
    
    if from_currency not in rates or to_currency not in rates:
        raise ValueError('Unsupported currency code.\nSupported codes are: ' + ', '.join(rates.keys()))

    return amount * rates[to_currency] / rates[from_currency]

def print_expenses(expenses, your_currency):
    print('+--------------+--------------+--------------+')
    print('|    Title     |    Amount    |    In ILS    |')
    print('+--------------+--------------+--------------+')
    total_ils = 0.0
    for title, amount, currency, converted in expenses:
        print('| {:12} | {:>8} {} | {:>8.2f} {} |'.format(title, amount, currency, converted, your_currency))
        total_ils += converted
    print('+--------------+--------------+--------------+')
    print('| Total        |              | {:>8.2f} {} |'.format(total_ils, your_currency))
    print('+--------------+--------------+--------------+')

if __name__ == "__main__":
    try:
        main()

    except ValueError as e:
        print(e)

