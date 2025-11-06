# day02 - Assignment

I wrote a Python app that prints and converts travel expenses to your currency, helping you track your budget.
The code uses a free and open-access API (https://www.exchangerate-api.com/docs/free) to get the current (updated once per day) exchange rates, and outputs your expenses in ILS (you can change the `your_currency` variable as needed).

The **CLI** code *travel_expences.py* was written manually and runs in one of two ways:
- By passing system arguments in triplets:
  
  `python travel_expences.py title1 amount1 currancy1 title2 amount2 currancy2 ...`

  Example: `python travel_expences.py Texi 160 ILS Flight 4000 USD Lunch 22.5 CHF`
  
- If no arguments are provided, it prompts you interactively to enter the triplets `title amount currancy` one by one (type `done` to finish).
  
I used ChatGPT-5 to build the **GUI** version, using the following prompt:

```
Following the attached script, write a new script for a GUI version.
On the top row: add input boxes for the title (str), amount (float), the currency (dropdown with the available currency codes), and a box with "+" to add the expense.
In the middle: show a table of all the added expenses with columns for the title, amount in the original currency, and the amount in the converted currency.
Bottom row: add a box to sum up the expenses and print the results.
Use similar logic and terminology to the attached code.
Use only Python standard libraries.
```

The provided code was then modified slightly to better fit my preferences, with almost no changes.
