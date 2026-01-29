# Expense Tracker CLI

A command-line expense tracking application with persistent storage in JSON format.

## Features

- Add expenses with date, category, amount, and notes
- List expenses with flexible filtering options
- Generate summaries with category breakdowns
- Edit and delete expenses
- Persistent storage in JSON format
- Input validation and error handling
- Logging to track operations

## Project Structure

```
tracker/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── cli.py               # Command-line interface
├── models.py            # Data models (Expense)
├── service.py           # Business logic layer
├── storage.py           # File storage operations
├── validation.py        # Input validation
└── logger.py            # Logging configuration

data/
└── expenses.json        # Persistent storage (auto-created)

logs/
└── tracker.log          # Application logs (auto-created)
```

## Installation

No external dependencies required! Uses only Python standard library.

Requires Python 3.7+

## Usage

### Add an Expense

```bash
# Add expense with all details
python -m tracker add --date 2026-01-26 --category food --amount 250.5 --note "Lunch"

# Add expense for today (date optional)
python -m tracker add --category transport --amount 80 --note "Rickshaw"

# Specify currency (default: BDT)
python -m tracker add --category rent --amount 400 --currency BDT --note "Room rent"
```

**Output:**
```
Added: EXP-20260126-0001 | 2026-01-26 | food | 250.50 BDT | Lunch
```

### List Expenses

```bash
# List all expenses
python -m tracker list

# Filter by month
python -m tracker list --month 2026-01

# Filter by category
python -m tracker list --category food

# Sort by amount (descending)
python -m tracker list --sort amount --desc

# Limit results
python -m tracker list --limit 10

```

**Output (table format):**
```
ID                    Date        Category   Amount      Note
-----------------------------------------------------------------
EXP-20260126-0001     2026-01-26  food       250.50 BDT  Lunch
EXP-20260125-0001     2026-01-25  transport  80.00 BDT   Rickshaw
```

### Summary

```bash
# Summary of all expenses
python -m tracker summary

```

**Output:**
```
Summary (2026-01)
Total expenses: 3
Grand total: 1210.50 BDT

By category:
  rent          400.00 BDT
  food          650.50 BDT
  transport     160.00 BDT
```

### Delete an Expense

```bash
python -m tracker delete --id EXP-20260126-0001
```

**Output:**
```
Deleted: EXP-20260126-0001
```

### Edit an Expense

```bash
# Edit amount and note
python -m tracker edit --id EXP-20260126-0001 --amount 300 --note "Lunch+coffee"

```

**Output:**
```
Updated: EXP-20260126-0001 | 2026-01-26 | food | 275.00 BDT | Lunch+coffee
```

## Arguments Reference

### `add` command

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `--date` | No | Date in YYYY-MM-DD format (default: today) | `--date 2026-01-26` |
| `--category` | Yes | Expense category | `--category food` |
| `--amount` | Yes | Amount (must be > 0) | `--amount 250.5` |
| `--note` | No | Optional description | `--note "Lunch"` |
| `--currency` | No | Currency code (default: BDT) | `--currency USD` |

### `list` command

| Argument | Description | Example |
|----------|-------------|---------|
| `--month` | Filter by month (YYYY-MM) | `--month 2026-01` |
| `--category` | Filter by category | `--category food` |
| `--sort` | Sort field (date/amount/category) | `--sort amount` |
| `--desc` | Sort descending | `--desc` |
| `--limit` | Limit results | `--limit 10` |


### `delete` command

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `--id` | Yes | Expense ID to delete | `--id EXP-20260126-0001` |

### `edit` command

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `--id` | Yes | Expense ID to edit | `--id EXP-20260126-0001` |
| `--category` | No | New category | `--category groceries` |
| `--amount` | No | New amount | `--amount 300` |
| `--note` | No | New note | `--note "Updated"` |

## Business Rules

1. **Date Format**: Must be YYYY-MM-DD
2. **Amount**: Must be greater than 0
3. **Category**: Required
4. **ID Generation**: Auto-generated in format `EXP-YYYYMMDD-NNNN`
5. **Currency**: Default is BDT
6. **Persistence**: All data stored in `data/expenses.json`

## Data Model

```json
{
  "version": 1,
  "expenses": [
    {
      "id": "EXP-20260126-0001",
      "date": "2026-01-26",
      "category": "food",
      "amount": 250.50,
      "currency": "BDT",
      "note": "Lunch",
      "created_at": "2026-01-26T12:30:45"
    }
  ]
}
```

## Error Handling

The application handles errors gracefully:

- **Invalid date format**: Shows "Error: date must be in YYYY-MM-DD format"
- **Invalid amount**: Shows "Error: amount must be > 0"
- **Missing category**: argparse shows usage error
- **Corrupted data file**: Shows clear error message
- **Missing expense**: Shows "Error: Expense not found"

All errors are logged to `logs/tracker.log`

## Logging

Application logs are stored in `logs/tracker.log`:

```
2026-01-26 12:30:45 - tracker.service - INFO - Adding expense: category=food, amount=250.5
2026-01-26 12:30:45 - tracker.storage - INFO - Added expense: EXP-20260126-0001
```

## Testing

Run the test commands from the assignment:

```bash
# Add test expenses
python -m tracker add --date 2026-01-25 --category transport --amount 80 --note "Rickshaw"
python -m tracker add --date 2026-01-26 --category food --amount 250.5 --note "Lunch"
python -m tracker add --date 2026-01-26 --category rent --amount 400 --note "Room rent"

# List all
python -m tracker list

# Generate summary
python -m tracker summary --month 2026-01
```
