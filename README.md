# Daily Expense Tracker

A simple, user-friendly Python application to track and manage your daily expenses efficiently.

## Features

✨ **Core Functionality:**
- ✅ **Add Expenses** - Record expenses with amount, category, and description
- ✅ **View All Expenses** - Display all expenses in a formatted table
- ✅ **Filter by Date** - View expenses for a specific date
- ✅ **Filter by Category** - View all expenses in a particular category
- ✅ **Category Summary** - Get total spending by category
- ✅ **Monthly Reports** - Analyze spending patterns by month
- ✅ **Delete Expenses** - Remove incorrect or duplicate entries
- ✅ **Data Persistence** - All expenses automatically saved to JSON file

## Installation

### Requirements
- Python 3.6+
- No external dependencies required!

### Setup
```bash
# Clone or download the repository
git clone https://github.com/vishu555/VishuFirstproject.git
cd VishuFirstproject

# Run the application
python main.py
```

## Usage

### Main Menu
When you run `python main.py`, you'll see an interactive menu:

```
==================================================
     DAILY EXPENSE TRACKER
==================================================
1. Add a new expense
2. View all expenses
3. Filter expenses by date
4. Filter expenses by category
5. View expense summary by category
6. View monthly summary
7. Delete an expense
8. Exit
==================================================
```

### Example Workflow

1. **Add an Expense:**
   - Select option 1
   - Enter amount: `25.50`
   - Enter category: `Food`
   - Enter description: `Lunch at cafe`
   - Leave date blank for today (or enter YYYY-MM-DD)

2. **View All Expenses:**
   - Select option 2
   - See formatted table of all recorded expenses

3. **Get Category Summary:**
   - Select option 5
   - View total spending by each category

4. **Monthly Report:**
   - Select option 6
   - Enter year: `2026`
   - Enter month: `02`
   - See spending breakdown for February 2026

## File Structure

```
VishuFirstproject/
├── main.py                 # Interactive menu interface
├── expense_tracker.py      # Core ExpenseTracker class
├── expenses.json          # Auto-generated data storage
└── README.md              # This file
```

## Data Format

Expenses are stored in `expenses.json` in the following format:

```json
[
  {
    "id": 1,
    "date": "2026-02-15",
    "amount": 25.50,
    "category": "Food",
    "description": "Lunch at cafe",
    "timestamp": "2026-02-15T10:30:45.123456"
  }
]
```

## Suggested Categories

- 🍔 **Food** - Groceries, restaurants, delivery
- 🚗 **Transport** - Gas, public transit, parking
- 🏠 **Utilities** - Electricity, water, internet
- 🎮 **Entertainment** - Movies, games, hobbies
- 📚 **Education** - Books, courses, training
- 💊 **Health** - Medical, gym membership
- 🛍️ **Shopping** - Clothes, accessories
- 💰 **Other** - Miscellaneous expenses

## Tips for Effective Tracking

1. **Be Consistent** - Log expenses daily for accurate tracking
2. **Use Clear Descriptions** - Make it easy to remember what you spent on
3. **Categorize Properly** - Use consistent categories for better analysis
4. **Review Monthly** - Check monthly summaries to identify spending patterns
5. **Budget Planning** - Use the data to set realistic budgets

## Example Commands

### Add multiple expenses:
```
Option 1 → Add 15.99 → Food → Coffee
Option 1 → Add 50.00 → Transport → Gas
Option 1 → Add 120.00 → Utilities → Electric bill
```

### View spending:
```
Option 5 → See total by category
Option 6 → Check spending for specific month
Option 3 → Review expenses on specific date
```

### Clean up:
```
Option 7 → Delete incorrect entries
```

## Data Persistence

- All data is automatically saved to `expenses.json`
- Your data persists between sessions
- You can backup your expenses by saving the `expenses.json` file

## Troubleshooting

**Issue:** Application won't start
- Solution: Make sure Python 3.6+ is installed: `python --version`

**Issue:** "expenses.json not found" error
- Solution: This is normal! The file is created automatically on first use

**Issue:** Date format error
- Solution: Use YYYY-MM-DD format (e.g., 2026-02-15)

## Future Enhancements

Potential features for future versions:
- 📊 Data visualization (charts/graphs)
- 📧 Email reports
- 💾 CSV export/import
- 🎯 Budget alerts
- 📱 Mobile app version
- 🔐 Password protection

## License

This project is open source and available for personal use.

## Contributing

Feel free to fork, modify, and improve this project!

---

**Happy Expense Tracking! 💰**