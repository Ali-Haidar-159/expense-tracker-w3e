"""
Command-line interface for the expense tracker.
"""

import argparse
import sys
from typing import List
from tracker.service import ExpenseService
from tracker.models import Expense
from tracker.logger import get_logger

logger = get_logger(__name__)


class ExpenseCLI:
    """Command-line interface for expense operations."""
    
    def __init__(self, service: ExpenseService):
        """
        Initialize CLI with service.
        
        Args:
            service: ExpenseService instance
        """
        self.service = service
    
    def format_expense_table(self, expenses: List[Expense]) -> str:
        """
        Format expenses as a table.
        
        Args:
            expenses: List of expenses to format
            
        Returns:
            Formatted table string
        """
        if not expenses:
            return "No expenses found."
        
        # Table headers
        headers = ["ID", "Date", "Category", "Amount", "Note"]
        
        # Calculate column widths
        col_widths = [
            max(len(headers[0]), max(len(exp.id) for exp in expenses)),
            max(len(headers[1]), 10),  # Date is always 10 chars
            max(len(headers[2]), max(len(exp.category) for exp in expenses)),
            max(len(headers[3]), 10),  # Amount column
            max(len(headers[4]), max(len(exp.note) for exp in expenses) if any(exp.note for exp in expenses) else 4)
        ]
        
        # Build table
        lines = []
        
        # Header row
        header_row = "  ".join(
            headers[i].ljust(col_widths[i]) for i in range(len(headers))
        )
        lines.append(header_row)
        lines.append("-" * len(header_row))
        
        # Data rows
        for exp in expenses:
            amount_str = f"{exp.amount:.2f} {exp.currency}"
            row = "  ".join([
                exp.id.ljust(col_widths[0]),
                exp.date.ljust(col_widths[1]),
                exp.category.ljust(col_widths[2]),
                amount_str.ljust(col_widths[3]),
                exp.note.ljust(col_widths[4])
            ])
            lines.append(row)
        
        return "\n".join(lines)
    
    def add(self, args):
        """Handle add command."""
        logger.info(f"CLI: add command called with args: {args}")
        
        try:
            expense = self.service.add_expense(
                date=args.date,
                category=args.category,
                amount=args.amount,
                note=args.note or "",
                currency=args.currency
            )
            
            print(f"Added: {expense}")
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            print(str(e), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def list(self, args):
        """Handle list command."""
        logger.info(f"CLI: list command called with args: {args}")
        
        try:
            expenses = self.service.list_expenses(
                month=args.month,
                from_date=args.from_date,
                to_date=args.to_date,
                category=args.category,
                min_amount=args.min,
                max_amount=args.max,
                sort_by=args.sort,
                descending=args.desc,
                limit=args.limit
            )
            
            # Format output
            if args.format == "table":
                print(self.format_expense_table(expenses))
            elif args.format == "csv":
                self._print_csv(expenses)
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            print(str(e), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _print_csv(self, expenses: List[Expense]):
        """Print expenses in CSV format."""
        if not expenses:
            print("No expenses found.")
            return
        
        # Header
        print("ID,Date,Category,Amount,Currency,Note")
        
        # Rows
        for exp in expenses:
            note_escaped = exp.note.replace('"', '""')
            print(f'{exp.id},{exp.date},{exp.category},{exp.amount:.2f},{exp.currency},"{note_escaped}"')
    
    def summary(self, args):
        """Handle summary command."""
        logger.info(f"CLI: summary command called with args: {args}")
        
        try:
            summary_data = self.service.summary(
                month=args.month,
                from_date=args.from_date,
                to_date=args.to_date,
                category=args.category
            )
            
            # Print summary
            print(f"\nSummary {summary_data['period']}")
            print(f"Total expenses: {summary_data['count']}")
            print(f"Grand total: {summary_data['grand_total']:.2f} {summary_data['currency']}")
            
            if summary_data['totals_by_category']:
                print("\nBy category:")
                # Sort categories by total (descending)
                sorted_categories = sorted(
                    summary_data['totals_by_category'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Calculate column widths
                max_category_len = max(len(cat) for cat, _ in sorted_categories)
                
                for category, total in sorted_categories:
                    print(f"  {category.ljust(max_category_len)}  {total:>10.2f} {summary_data['currency']}")
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            print(str(e), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def delete(self, args):
        """Handle delete command."""
        logger.info(f"CLI: delete command called with args: {args}")
        
        try:
            result = self.service.delete_expense(args.id)
            
            if result:
                print(f"Deleted: {args.id}")
            else:
                print(f"Error: Expense not found: {args.id}", file=sys.stderr)
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def edit(self, args):
        """Handle edit command."""
        logger.info(f"CLI: edit command called with args: {args}")
        
        try:
            # Check if at least one field is provided
            if not any([args.date, args.category, args.amount, args.note, args.currency]):
                print("Error: At least one field must be provided to edit", file=sys.stderr)
                sys.exit(1)
            
            result = self.service.edit_expense(
                expense_id=args.id,
                date=args.date,
                category=args.category,
                amount=args.amount,
                note=args.note,
                currency=args.currency
            )
            
            if result:
                print(f"Updated: {result}")
            else:
                print(f"Error: Expense not found: {args.id}", file=sys.stderr)
                sys.exit(1)
                
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            print(str(e), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Personal expense tracker CLI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--date", help="Date (YYYY-MM-DD, default: today)")
    add_parser.add_argument("--category", required=True, help="Category (e.g., food, transport)")
    add_parser.add_argument("--amount", required=True, type=float, help="Amount spent")
    add_parser.add_argument("--note", help="Optional note")
    add_parser.add_argument("--currency", default="BDT", help="Currency code (default: BDT)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List expenses with filters")
    list_parser.add_argument("--month", help="Filter by month (YYYY-MM)")
    list_parser.add_argument("--from", dest="from_date", help="From date (YYYY-MM-DD)")
    list_parser.add_argument("--to", dest="to_date", help="To date (YYYY-MM-DD)")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--min", type=float, help="Minimum amount")
    list_parser.add_argument("--max", type=float, help="Maximum amount")
    list_parser.add_argument("--sort", choices=["date", "amount", "category"], default="date", help="Sort by field")
    list_parser.add_argument("--desc", action="store_true", help="Sort in descending order")
    list_parser.add_argument("--limit", type=int, help="Limit number of results")
    list_parser.add_argument("--format", choices=["table", "csv"], default="table", help="Output format")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show expense summary")
    summary_parser.add_argument("--month", help="Filter by month (YYYY-MM)")
    summary_parser.add_argument("--from", dest="from_date", help="From date (YYYY-MM-DD)")
    summary_parser.add_argument("--to", dest="to_date", help="To date (YYYY-MM-DD)")
    summary_parser.add_argument("--category", help="Filter by category")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an expense")
    delete_parser.add_argument("--id", required=True, help="Expense ID to delete")
    
    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit an expense")
    edit_parser.add_argument("--id", required=True, help="Expense ID to edit")
    edit_parser.add_argument("--date", help="New date (YYYY-MM-DD)")
    edit_parser.add_argument("--category", help="New category")
    edit_parser.add_argument("--amount", type=float, help="New amount")
    edit_parser.add_argument("--note", help="New note")
    edit_parser.add_argument("--currency", help="New currency")
    
    return parser


def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize service and CLI
    service = ExpenseService()
    cli = ExpenseCLI(service)
    
    # Dispatch to appropriate handler
    if args.command == "add":
        cli.add(args)
    elif args.command == "list":
        cli.list(args)
    elif args.command == "summary":
        cli.summary(args)
    elif args.command == "delete":
        cli.delete(args)
    elif args.command == "edit":
        cli.edit(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()