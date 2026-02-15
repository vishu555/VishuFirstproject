import json
import os
from datetime import datetime
from pathlib import Path

class ExpenseTracker:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = self.load_expenses()
    
    def load_expenses(self):
        """Load expenses from JSON file."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return []
    
    def save_expenses(self):
        """Save expenses to JSON file."""
        with open(self.filename, 'w') as f:
            json.dump(self.expenses, f, indent=2)
    
    def add_expense(self, amount, category, description, date=None):
        """Add a new expense."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        expense = {
            "id": len(self.expenses) + 1,
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        self.expenses.append(expense)
        self.save_expenses()
        print(f"✓ Expense added: {category} - ${amount:.2f}")
        return expense
    
    def view_all_expenses(self):
        """Display all expenses."""
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        print("\n" + "="*70)
        print(f"{'ID':<5} {'Date':<12} {'Category':<15} {'Amount':<10} {'Description':<25}")
        print("="*70)
        for exp in self.expenses:
            print(f"{exp['id']:<5} {exp['date']:<12} {exp['category']:<15} ${exp['amount']:<9.2f} {exp['description']:<25}")
        print("="*70)
    
    def view_expenses_by_date(self, date):
        """View expenses for a specific date."""
        filtered = [e for e in self.expenses if e['date'] == date]
        if not filtered:
            print(f"No expenses found for {date}.")
            return
        
        print(f"\nExpenses for {date}:")
        print("-" * 50)
        for exp in filtered:
            print(f"{exp['category']}: ${exp['amount']:.2f} - {exp['description']}")
    
    def view_expenses_by_category(self, category):
        """View expenses for a specific category."""
        filtered = [e for e in self.expenses if e['category'].lower() == category.lower()]
        if not filtered:
            print(f"No expenses found in {category} category.")
            return
        
        print(f"\nExpenses in {category}:")
        print("-" * 50)
        total = 0
        for exp in filtered:
            print(f"{exp['date']}: ${exp['amount']:.2f} - {exp['description']}")
            total += exp['amount']
        print("-" * 50)
        print(f"Total: ${total:.2f}")
    
    def get_summary(self):
        """Get expense summary by category."""
        if not self.expenses:
            print("No expenses to summarize.")
            return
        
        summary = {}
        for exp in self.expenses:
            category = exp['category']
            summary[category] = summary.get(category, 0) + exp['amount']
        
        print("\n" + "="*40)
        print("EXPENSE SUMMARY BY CATEGORY")
        print("="*40)
        total = 0
        for category, amount in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{category:<20} ${amount:>10.2f}")
            total += amount
        print("-"*40)
        print(f"{'TOTAL':<20} ${total:>10.2f}")
        print("="*40)
    
    def get_monthly_summary(self, year, month):
        """Get summary for a specific month."""
        filtered = [e for e in self.expenses if e['date'].startswith(f"{year}-{month:02d}")]
        
        if not filtered:
            print(f"No expenses found for {year}-{month:02d}.")
            return
        
        summary = {}
        total = 0
        for exp in filtered:
            category = exp['category']
            summary[category] = summary.get(category, 0) + exp['amount']
            total += exp['amount']
        
        print(f"\nExpense Summary for {year}-{month:02d}")
        print("="*40)
        for category, amount in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{category:<20} ${amount:>10.2f}")
        print("-"*40)
        print(f"{'TOTAL':<20} ${total:>10.2f}")
        print("="*40)
    
    def delete_expense(self, expense_id):
        """Delete an expense by ID."""
        self.expenses = [e for e in self.expenses if e['id'] != expense_id]
        self.save_expenses()
        print(f"✓ Expense with ID {expense_id} deleted.")
    
    def get_total_expenses(self):
        """Get total of all expenses."""
        return sum(e['amount'] for e in self.expenses)