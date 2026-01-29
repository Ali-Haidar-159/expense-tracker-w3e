"""
Business logic layer for expense operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from tracker.models import Expense
from tracker.storage import ExpenseStorage
from tracker.validation import format_date, format_amount, format_category
from tracker.logger import get_logger

logger = get_logger(__name__)


class ExpenseService:
    """Service layer for expense business logic."""
    
    def __init__(self, storage: Optional[ExpenseStorage] = None):
        """
        Initialize service with storage.
        
        Args:
            storage: ExpenseStorage instance (creates default if None)
        """
        self.storage = storage or ExpenseStorage()
    
    def generate_id(self, date: str) -> str:
        """
        Generate unique expense ID.
        
        Format: EXP-YYYYMMDD-NNNN
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            Unique expense ID
        """
        # Get all expenses for the same date
        all_expenses = self.storage.load_all()
        date_prefix = f"EXP-{date.replace('-', '')}"
        
        # Find highest sequence number for this date
        max_seq = 0
        for exp in all_expenses:
            if exp.id.startswith(date_prefix):
                try:
                    seq = int(exp.id.split('-')[-1])
                    max_seq = max(max_seq, seq)
                except ValueError:
                    continue
        
        # Generate new ID with next sequence number
        new_seq = max_seq + 1
        return f"{date_prefix}-{new_seq:04d}"
    
    def add_expense(
        self,
        date: Optional[str] = None,
        category: str = "",
        amount: float = 0.0,
        note: str = "",
        currency: str = "BDT"
    ) -> Expense:
        """
        Add a new expense.
        
        Args:
            date: Date of expense (YYYY-MM-DD or None for today)
            category: Category of expense
            amount: Amount spent
            note: Optional note
            currency: Currency code
            
        Returns:
            Created Expense object
            
        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Adding expense: category={category}, amount={amount}")
        
        # Validate and format inputs
        formatted_date = format_date(date)
        formatted_amount = format_amount(amount)
        formatted_category = format_category(category)
        
        # Generate ID and timestamp
        expense_id = self.generate_id(formatted_date)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create expense
        expense = Expense(
            id=expense_id,
            date=formatted_date,
            category=formatted_category,
            amount=formatted_amount,
            currency=currency,
            note=note.strip(),
            created_at=created_at
        )
        
        # Save to storage
        self.storage.add(expense)
        logger.info(f"Successfully added expense: {expense_id}")
        
        return expense
    
    def list_expenses(
        self,
        month: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "date",
        descending: bool = False,
        limit: Optional[int] = None
    ) -> List[Expense]:
        """
        List expenses with filters.
        
        Args:
            month: Filter by month (YYYY-MM format)
            from_date: Filter from date (inclusive)
            to_date: Filter to date (inclusive)
            category: Filter by category (exact match or case-insensitive)
            min_amount: Minimum amount filter
            max_amount: Maximum amount filter
            sort_by: Field to sort by (date, amount, category)
            descending: Sort in descending order
            limit: Maximum number of results
            
        Returns:
            Filtered and sorted list of expenses
        """
        logger.info(f"Listing expenses with filters: month={month}, category={category}")
        
        expenses = self.storage.load_all()
        
        # Apply filters
        filtered = self._apply_filters(
            expenses,
            month=month,
            from_date=from_date,
            to_date=to_date,
            category=category,
            min_amount=min_amount,
            max_amount=max_amount
        )
        
        # Sort
        sorted_expenses = self._sort_expenses(filtered, sort_by, descending)
        
        # Apply limit
        if limit and limit > 0:
            sorted_expenses = sorted_expenses[:limit]
        
        logger.info(f"Returning {len(sorted_expenses)} expenses")
        return sorted_expenses
    
    def _apply_filters(
        self,
        expenses: List[Expense],
        month: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Expense]:
        """Apply filters to expense list."""
        filtered = expenses
        
        # Month filter
        if month:
            filtered = [exp for exp in filtered if exp.date.startswith(month)]
        
        # Date range filters
        if from_date:
            filtered = [exp for exp in filtered if exp.date >= from_date]
        if to_date:
            filtered = [exp for exp in filtered if exp.date <= to_date]
        
        # Category filter (case-insensitive)
        if category:
            category_lower = category.lower()
            filtered = [exp for exp in filtered if exp.category.lower() == category_lower]
        
        # Amount filters
        if min_amount is not None:
            filtered = [exp for exp in filtered if exp.amount >= min_amount]
        if max_amount is not None:
            filtered = [exp for exp in filtered if exp.amount <= max_amount]
        
        return filtered
    
    def _sort_expenses(
        self,
        expenses: List[Expense],
        sort_by: str,
        descending: bool
    ) -> List[Expense]:
        """Sort expenses by specified field."""
        if sort_by == "amount":
            return sorted(expenses, key=lambda x: x.amount, reverse=descending)
        elif sort_by == "category":
            return sorted(expenses, key=lambda x: x.category, reverse=descending)
        else:  # Default to date
            return sorted(expenses, key=lambda x: x.date, reverse=descending)
    
    def summary(
        self,
        month: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate expense summary.
        
        Args:
            month: Filter by month (YYYY-MM format)
            from_date: Filter from date (inclusive)
            to_date: Filter to date (inclusive)
            category: Filter by category
            
        Returns:
            Dictionary with summary statistics:
                - count: Total number of expenses
                - grand_total: Sum of all amounts
                - totals_by_category: Dict of category -> total amount
                - currency: Currency code
                - period: Description of period
        """
        logger.info(f"Generating summary: month={month}, category={category}")
        
        # Get filtered expenses
        expenses = self.list_expenses(
            month=month,
            from_date=from_date,
            to_date=to_date,
            category=category
        )
        
        if not expenses:
            return {
                "count": 0,
                "grand_total": 0.0,
                "totals_by_category": {},
                "currency": "BDT",
                "period": self._get_period_description(month, from_date, to_date)
            }
        
        # Calculate totals
        grand_total = sum(exp.amount for exp in expenses)
        currency = expenses[0].currency  # Assume all same currency
        
        # Calculate category totals
        category_totals = {}
        for exp in expenses:
            if exp.category not in category_totals:
                category_totals[exp.category] = 0.0
            category_totals[exp.category] += exp.amount
        
        return {
            "count": len(expenses),
            "grand_total": grand_total,
            "totals_by_category": category_totals,
            "currency": currency,
            "period": self._get_period_description(month, from_date, to_date)
        }
    
    def _get_period_description(
        self,
        month: Optional[str],
        from_date: Optional[str],
        to_date: Optional[str]
    ) -> str:
        """Get human-readable period description."""
        if month:
            return f"({month})"
        elif from_date and to_date:
            return f"({from_date} to {to_date})"
        elif from_date:
            return f"(from {from_date})"
        elif to_date:
            return f"(to {to_date})"
        else:
            return "(all time)"
    
    def delete_expense(self, expense_id: str) -> bool:
        """
        Delete an expense by ID.
        
        Args:
            expense_id: ID of expense to delete
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting expense: {expense_id}")
        result = self.storage.delete(expense_id)
        
        if result:
            logger.info(f"Successfully deleted expense: {expense_id}")
        else:
            logger.warning(f"Expense not found: {expense_id}")
        
        return result
    
    def edit_expense(
        self,
        expense_id: str,
        date: Optional[str] = None,
        category: Optional[str] = None,
        amount: Optional[float] = None,
        note: Optional[str] = None,
        currency: Optional[str] = None
    ) -> Optional[Expense]:
        """
        Edit an existing expense.
        
        Args:
            expense_id: ID of expense to edit
            date: New date (optional)
            category: New category (optional)
            amount: New amount (optional)
            note: New note (optional)
            currency: New currency (optional)
            
        Returns:
            Updated Expense object or None if not found
        """
        logger.info(f"Editing expense: {expense_id}")
        
        # Build updates dictionary
        updates = {}
        
        if date is not None:
            updates["date"] = format_date(date)
        if category is not None:
            updates["category"] = format_category(category)
        if amount is not None:
            updates["amount"] = format_amount(amount)
        if note is not None:
            updates["note"] = note.strip()
        if currency is not None:
            updates["currency"] = currency
        
        # Update in storage
        result = self.storage.update(expense_id, updates)
        
        if result:
            logger.info(f"Successfully edited expense: {expense_id}")
        else:
            logger.warning(f"Expense not found: {expense_id}")
        
        return result