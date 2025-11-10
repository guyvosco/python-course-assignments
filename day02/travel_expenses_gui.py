#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import json
from day02.travel_expenses import exchange_rates

API_URL = 'https://open.er-api.com/v6/latest/USD'
YOUR_CURRENCY = 'ILS'

class ExpenseGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Converter")
        self.geometry("680x460")
        self.resizable(False, False)

        self.rates = {}
        self.expenses = []

        self._build_inputs_row()
        self._build_table()
        self._build_sum_row()

        self._load_rates()

    def _build_inputs_row(self):
        frm = ttk.Frame(self, padding=(12, 12, 12, 6))
        frm.grid(row=0, column=0, sticky="ew")
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)

        ttk.Label(frm, text="Title").grid(row=0, column=0, padx=(0, 8))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(frm, textvariable=self.title_var, width=24)
        self.title_entry.grid(row=0, column=1, padx=(0, 16))

        ttk.Label(frm, text="Amount").grid(row=0, column=2, padx=(0, 8))
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(frm, textvariable=self.amount_var, width=12)
        self.amount_entry.grid(row=0, column=3, padx=(0, 16))

        ttk.Label(frm, text="Currency").grid(row=0, column=4, padx=(0, 8))
        self.currency_var = tk.StringVar()
        self.currency_combo = ttk.Combobox(frm, textvariable=self.currency_var, width=10, state="readonly")
        self.currency_combo.grid(row=0, column=5)

        self.add_btn = ttk.Button(frm, text="+", width=3, command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=(16, 0))
        self.msg_var = tk.StringVar(value="")
        self.msg_label = ttk.Label(frm, textvariable=self.msg_var, foreground="#cc0000")
        self.msg_label.grid(row=1, column=0)

    def _build_table(self):
        frm = ttk.Frame(self, padding=(12, 6, 12, 6))
        frm.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        columns = ("title", "amount", "currency", "converted")
        self.tree = ttk.Treeview(frm, columns=columns, show="headings", height=12)
        self.tree.heading("title", text="Title")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("currency", text="Currency")
        self.tree.heading("converted", text=f"In {YOUR_CURRENCY}")

        self.tree.column("title", width=240, anchor="w")
        self.tree.column("amount", width=100, anchor="e")
        self.tree.column("currency", width=100, anchor="center")
        self.tree.column("converted", width=140, anchor="e")

        vsb = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        frm.rowconfigure(0, weight=1)
        frm.columnconfigure(0, weight=1)

    def _build_sum_row(self):
        frm = ttk.Frame(self, padding=(12, 6, 12, 12))
        frm.grid(row=3, column=0, sticky="ew")
        frm.columnconfigure(2, weight=1)

        ttk.Button(frm, text="Sum", command=self.sum_expenses).grid(row=0, column=0, padx=(0, 8))
        ttk.Label(frm, text=f"Total ({YOUR_CURRENCY})").grid(row=0, column=1, padx=(8, 8))
        self.total_var = tk.StringVar(value="0.00")
        self.total_entry = ttk.Entry(frm, textvariable=self.total_var, width=16, state="readonly", justify="right")
        self.total_entry.grid(row=0, column=2, sticky="e")

        ttk.Button(frm, text="Remove selected", command=self.remove_selected).grid(row=0, column=3, padx=(16, 0))

    def _load_rates(self):
        try:
            self.rates = json.loads(urllib.request.urlopen(API_URL).read())['rates']
            codes = sorted(self.rates.keys())
            self.currency_combo["values"] = codes
            self.currency_combo.set("USD" if "USD" in codes else codes[0])
            self.msg_var.set("")
        except Exception as e:
            self.rates = {}
            self.currency_combo["values"] = []
            self.msg_var.set("Failed to load currency codes. Check your internet connection.")
            messagebox.showerror("Error", f"Could not fetch currency rates:\n{e}")

    def add_expense(self):
        title = self.title_var.get().strip()
        amount_str = self.amount_var.get().strip()
        currency = self.currency_var.get().strip()

        if not title:
            self.msg_var.set("Title is required.")
            self.title_entry.focus_set()
            return
        if not amount_str:
            self.msg_var.set("Amount is required.")
            self.amount_entry.focus_set()
            return
        if not currency:
            self.msg_var.set("Choose a currency code.")
            self.currency_combo.focus_set()
            return

        try:
            converted = exchange_rates(self.rates,amount_str, currency, YOUR_CURRENCY)
        except ValueError as ve:
            self.msg_var.set(str(ve))
            return
        except Exception as e:
            self.msg_var.set("Conversion failed. Try again.")
            messagebox.showerror("Error", f"Conversion failed:\n{e}")
            return

        amount = float(amount_str)
        self.expenses.append({
            "title": title,
            "amount": amount,
            "currency": currency,
            "converted": converted
        })

        self.tree.insert("", "end", values=(title, f"{amount:.2f}", currency, f"{converted:.2f}"))
        self.msg_var.set("Added.")
        self._clear_inputs()

    def _clear_inputs(self):
        self.title_var.set("")
        self.amount_var.set("")
        self.title_entry.focus_set()

    def sum_expenses(self):
        total = sum(item["converted"] for item in self.expenses)
        self.total_var.set(f"{total:.2f}")

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for item_id in sel:
            vals = self.tree.item(item_id, "values")
            key = (vals[0], float(vals[1]), vals[2], float(vals[3]))
            for i, exp in enumerate(self.expenses):
                if (exp["title"], round(exp["amount"], 2), exp["currency"], round(exp["converted"], 2)) == \
                   (key[0], round(key[1], 2), key[2], round(key[3], 2)):
                    self.expenses.pop(i)
                    break
            self.tree.delete(item_id)

        self.sum_expenses()

if __name__ == "__main__":
    app = ExpenseGUI()
    app.mainloop()
