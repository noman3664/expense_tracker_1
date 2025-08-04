import pandas as pd
import os
from datetime import date


class Expense:
    # constructor
    def __init__(self, amount, category, date, note):
        self.amount = amount
        self.category = category
        self.date = date
        self.note = note


class ExpenseManager:
    def __init__(self, file_path="expenses.csv"):
        self.file_path = file_path
        self.expenses = []
        self.ensure_file_initialized()  # ensures the CSV file is initialized
        self.load_expenses()  # reads from CSV and creates objects.

    def add_expense(self, expense):
        self.expenses.append(expense)
        # saves to CSV. Writes it to CSV (without overwriting)
        self.save_to_csv(expense)

    def remove_expense(self, index):
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
        self.save_all_to_csv()

    def edit_expense(self, index, new_expense):
        if 0 <= index < len(self.expenses):
            self.expenses[index] = new_expense
        self.save_all_to_csv()

    def save_all_to_csv(self):
        df = pd.DataFrame([vars(e) for e in self.expenses])
        df.to_csv(self.file_path, index=False)

    def save_to_csv(self, expense):
        df = pd.DataFrame([{
            'amount': expense.amount,
            'category': expense.category,
            'date': expense.date,
            'note': expense.note
        }])         # append to CSV file
        write_header = not os.path.exists(
            self.file_path) or os.stat(self.file_path).st_size == 0

        df.to_csv(self.file_path, mode='a', header=write_header, index=False)
        print(
            f"Expense added: {expense.amount} in {expense.category} on {expense.date}")

    def load_expenses(self):
        if not os.path.exists(self.file_path) or os.stat(self.file_path).st_size == 0:
            print(
                "CSV file does not exist or is empty. Starting with empty expense list.")
            self.expenses = []
            return

        try:
            df = pd.read_csv(self.file_path)
            if 'date' not in df.columns:
                raise ValueError("CSV missing 'date' column.")

            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            for _, row in df.iterrows():
                self.expenses.append(
                    Expense(row['amount'], row['category'],
                            row['date'], row.get('note', ''))
                )
        except Exception as e:
            print(f"Error reading CSV: {str(e)}")
            self.expenses = []

    def get_all_expenses(self):
        return self.expenses

    def ensure_file_initialized(self):
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=["amount", "category", "date", "note"])
            df.to_csv(self.file_path, index=False)

    def filter_expenses(self, category=None, start_date=None, end_date=None):
        filtered = self.expenses
        if category:
            filtered = [e for e in filtered if e.category == category]
        if start_date:
            filtered = [e for e in filtered if pd.to_datetime(
                e.date).date() >= start_date]
        if end_date:
            filtered = [e for e in filtered if pd.to_datetime(
                e.date).date() <= end_date]
        return filtered
        # get summary of expenses by category

    def get_summary(self):
        df = pd.DataFrame([vars(e) for e in self.expenses])
        summary = df.groupby('category')['amount'].sum().reset_index()
        return summary
