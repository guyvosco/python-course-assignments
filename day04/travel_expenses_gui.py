#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from utilities import exchange_rates, get_currency_rates

DEFAULT_CURRENCY = 'ILS'

class ExpenseGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Converter")
        self.geometry("680x460")
        self.resizable(False, False)

        self.rates = {}
        self.expenses = []
        self.last_update = ""
        self.your_currency = tk.StringVar(value = DEFAULT_CURRENCY)

        self._build_inputs_row()
        self._build_table()
        self._build_sum_row()

        self._load_rates()

    def _build_inputs_row(self):
        frm = ttk.Frame(self, padding=(12, 12, 12, 12))
        frm.grid(row=0, column=0, sticky="ew")
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)
        frm.columnconfigure(5, weight=1)
        frm.columnconfigure(6, weight=1)

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
        self.currency_combo = ttk.Combobox(frm, textvariable=self.currency_var, width=12, state="readonly")
        self.currency_combo.grid(row=0, column=5)

        ttk.Button(frm, text="+", width=8, command=self.add_expense).grid(row=0, column=6, padx=(16, 0))
        self.msg_var = tk.StringVar(value="")
        self.msg_label = ttk.Label(frm, textvariable=self.msg_var, foreground="#cc0000").grid(row=1, column=0, columnspan=5, sticky="w")

        ttk.Button(frm, text="del", width=8, command=self.remove_selected).grid(row=1, column=6, padx=(16, 0))
        self.msg_var = tk.StringVar(value="")
        self.msg_label = ttk.Label(frm, textvariable=self.msg_var, foreground="#cc0000").grid(row=1, column=0, columnspan=5, sticky="w")

    def _build_table(self):
        frm = ttk.Frame(self, padding=(12, 12, 12, 12))
        frm.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        columns = ("title", "amount", "currency", "converted")
        self.tree = ttk.Treeview(frm, columns=columns, show="headings", height=12)
        self.tree.heading("title", text="Title")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("currency", text="Currency")
        self.tree.heading("converted", text=f"In {self.your_currency}")

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
        frm = ttk.Frame(self, padding=(12, 12, 12, 12))
        frm.grid(row=3, column=0, sticky="ew")
        frm.columnconfigure(5, weight=1)

        ttk.Label(frm, text="Your currency").grid(row=0, column=0, padx=(0, 8))
        self.target_currency_combo = ttk.Combobox(frm, textvariable=self.your_currency, width=8, state="readonly")
        self.target_currency_combo.grid(row=0, column=1, padx=(0, 8))
        self.target_currency_combo.bind("<<ComboboxSelected>>", lambda _e: self._on_target_currency_change())

        ttk.Button(frm, text="Sum", command=self.sum_expenses).grid(row=0, column=2, padx=(0, 8))
        self.total_label = ttk.Label(frm, text=f"Total ({self.your_currency.get()})")
        self.total_label.grid(row=0, column=3, padx=(8, 8))
        self.total_var = tk.StringVar(value="0.00")
        self.total_entry = ttk.Entry(frm, textvariable=self.total_var, width=12, state="readonly", justify="right")
        self.total_entry.grid(row=0, column=4, sticky="e")

        ttk.Button(frm, text="Reload rates", command=self.refresh_rates).grid(row=0, column=6, padx=(16, 0))

    def _load_rates(self, refresh = False):
        try:
            data = get_currency_rates(refresh)
            self.rates = data['rates']
            self.last_update = data.get('time_last_update_utc', '')
            self.title(f"Expense Converter - Last update: {self.last_update}")
            codes = sorted(self.rates.keys())
            self.currency_combo["values"] = codes
            self.target_currency_combo["values"] = codes
            if self.your_currency.get() not in codes:
                self.your_currency.set("ILS" if "ILS" in codes else ("USD" if "USD" in codes else codes[0]))
            self.currency_combo.set("USD" if "USD" in codes else codes[0])
            self._update_headings()
            self.recalculate_all()
            self.msg_var.set("")
        except Exception as e:
            self.rates = {}
            self.currency_combo["values"] = []
            self.target_currency_combo["values"] = []
            self.msg_var.set("Failed to load currency codes.")
            messagebox.showerror("Error", f"Could not fetch currency rates:\n{e}")

    def refresh_rates(self):
        self._load_rates(refresh=True)

    def _update_headings(self):
        self.tree.heading("converted", text=f"In {self.your_currency.get()}")
        self.total_label.configure(text=f"Total ({self.your_currency.get()})")

    def _on_target_currency_change(self):
        self._update_headings()
        self.recalculate_all()

    def add_expense(self):
        title = self.title_var.get().strip()
        amount_str = self.amount_var.get().strip()
        currency = self.currency_var.get().strip()
        target_currency = self.your_currency.get().strip()

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
            converted = exchange_rates(self.rates, amount_str, currency, target_currency)
        except ValueError as ve:
            self.msg_var.set(str(ve))
            return
        except Exception as e:
            self.msg_var.set("Conversion failed.")
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

    def recalculate_all(self):
        if not self.expenses or not self.rates:
            self.sum_expenses()
            return
        target = self.your_currency.get()
        children = list(self.tree.get_children())
        for i, exp in enumerate(self.expenses):
            try:
                converted = exchange_rates(self.rates, exp["amount"], exp["currency"], target)
            except Exception:
                converted = 0.0
            exp["converted"] = converted
            if i < len(children):
                self.tree.item(children[i], values=(
                    exp["title"], f"{exp['amount']:.2f}", exp["currency"], f"{converted:.2f}"
                ))
        self.sum_expenses()

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        to_remove = []
        for item_id in sel:
            vals = self.tree.item(item_id, "values")
            for i, exp in enumerate(self.expenses):
                if (exp["title"], f"{exp['amount']:.2f}", exp["currency"], f"{exp['converted']:.2f}") == tuple(vals):
                    to_remove.append(i)
                    break
            self.tree.delete(item_id)
        for idx in sorted(to_remove, reverse=True):
            self.expenses.pop(idx)
        self.sum_expenses()
        self.msg_var.set("Removed.")

if __name__ == "__main__":
    app = ExpenseGUI()
    app.mainloop()
