import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "expenses.json"


class ExpenseTracker(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Трекер расходов")
        self.geometry("750px550")
        self.expenses = []
        self.load_data()
        self.init_ui()
        self.update_table(self.expenses)

    def init_ui(self):
        # --- Блок ввода (Изменено на ttk.LabelFrame) ---
        input_frame = ttk.LabelFrame(self, text="Добавить новый расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w")
        self.category_combobox = ttk.Combobox(
            input_frame, values=["Еда", "Транспорт", "Развлечения", "Одежда", "Другое"]
        )
        self.category_combobox.grid(row=0, column=3, padx=5, pady=2)
        self.category_combobox.current(0)

        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(
            row=0, column=4, sticky="w"
        )
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.grid(row=0, column=5, padx=5, pady=2)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        add_btn = tk.Button(
            input_frame, text="Добавить расход", command=self.add_expense
        )
        add_btn.grid(row=0, column=6, padx=10)

        # --- Блок фильтров (Изменено на ttk.LabelFrame) ---
        filter_frame = ttk.LabelFrame(self, text="Фильтрация и анализ", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w")
        self.filter_cat = ttk.Combobox(
            filter_frame,
            values=["Все", "Еда", "Транспорт", "Развлечения", "Одежда", "Другое"],
        )
        self.filter_cat.grid(row=0, column=1, padx=5, pady=2)
        self.filter_cat.current(0)

        tk.Label(filter_frame, text="С даты:").grid(row=0, column=2, sticky="w")
        self.filter_start_date = tk.Entry(filter_frame, width=12)
        self.filter_start_date.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(filter_frame, text="По дату:").grid(row=0, column=4, sticky="w")
        self.filter_end_date = tk.Entry(filter_frame, width=12)
        self.filter_end_date.grid(row=0, column=5, padx=5, pady=2)

        action_frame = tk.Frame(filter_frame)
        action_frame.grid(row=0, column=6, padx=10, columnspan=2)

        filter_btn = tk.Button(action_frame, text="Применить", command=self.apply_filter)
        filter_btn.pack(side="left", padx=2)

        reset_btn = tk.Button(action_frame, text="Сбросить", command=self.reset_filter)
        reset_btn.pack(side="left", padx=2)

        # --- Блок вывода (Таблица) ---
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "category", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Блок Итогов ---
        self.total_label = tk.Label(
            self, text="Итого за период: 0.00", font=("Arial", 12, "bold")
        )
        self.total_label.pack(anchor="e", padx=10, pady=10)

    def validate_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_combobox.get()
        date_str = self.date_entry.get().strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Ошибка ввода", "Сумма должна быть положительным числом!"
            )
            return

        if not self.validate_date(date_str):
            messagebox.showerror(
                "Ошибка ввода", "Неверный формат даты! Используйте ГГГГ-ММ-ДД."
            )
            return

        expense = {"amount": amount, "category": category, "date": date_str}
        self.expenses.append(expense)
        self.save_data()

        self.reset_filter()
        self.amount_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Расход успешно добавлен!")

    def apply_filter(self):
        cat_filter = self.filter_cat.get()
        start_str = self.filter_start_date.get().strip()
        end_str = self.filter_end_date.get().strip()

        filtered = self.expenses

        if cat_filter != "Все":
            filtered = [x for x in filtered if x["category"] == cat_filter]

        if start_str:
            if not self.validate_date(start_str):
                messagebox.showerror("Ошибка даты", "Неверный формат начальной даты.")
                return
            filtered = [x for x in filtered if x["date"] >= start_str]

        if end_str:
            if not self.validate_date(end_str):
                messagebox.showerror("Ошибка даты", "Неверный формат конечной даты.")
                return
            filtered = [x for x in filtered if x["date"] <= end_str]

        self.update_table(filtered)

    def reset_filter(self):
        self.filter_cat.current(0)
        self.filter_start_date.delete(0, tk.END)
        self.filter_end_date.delete(0, tk.END)
        self.update_table(self.expenses)

    def update_table(self, data_list):
        for item in self.tree.get_children():
            self.tree.delete(item)

        sorted_data = sorted(data_list, key=lambda x: x["date"], reverse=True)

        total = 0.0
        for exp in sorted_data:
            self.tree.insert(
                "", tk.END, values=(exp["date"], exp["category"], f"{exp['amount']:.2f}")
            )
            total += exp["amount"]

        self.total_label.config(text=f"Итого за период: {total:.2f}")

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except json.JSONDecodeError:
                self.expenses = []


if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()
