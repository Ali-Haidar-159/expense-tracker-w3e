"""
Storage layer for persisting expenses to JSON file.
"""

import json
import os
from typing import List, Optional
from pathlib import Path
from tracker.models import Expense
from tracker.logger import get_logger

logger = get_logger(__name__)


class ExpenseStorage:
    """Handles reading and writing expenses to JSON file."""
    
    def __init__(self, filepath: str = "data/expenses.json"):
        """
        Initialize storage with file path.
        
        Args:
            filepath: Path to JSON file for storing expenses
        """
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the data directory and file if they don't exist."""
        try:
            # Create directory if it doesn't exist
            Path(self.filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Create file with initial structure if it doesn't exist
            if not os.path.exists(self.filepath):
                initial_data = {
                    "version": 1,
                    "expenses": []
                }
                with open(self.filepath, 'w') as f:
                    json.dump(initial_data, f, indent=2)
                logger.info(f"Created new data file: {self.filepath}")
        except Exception as e:
            logger.error(f"Failed to ensure file exists: {e}")
            raise
    
    def load_all(self) -> List[Expense]:
        """
        Load all expenses from file.
        
        Returns:
            List of Expense objects
        """
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                expenses_data = data.get("expenses", [])
                expenses = [Expense.from_dict(exp) for exp in expenses_data]
                logger.info(f"Loaded {len(expenses)} expenses from file")
                return expenses
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON file: {e}")
            raise ValueError(f"Error: Data file is corrupted. Please check {self.filepath}")
        except FileNotFoundError:
            logger.warning(f"File not found: {self.filepath}")
            self._ensure_file_exists()
            return []
        except Exception as e:
            logger.error(f"Failed to load expenses: {e}")
            raise ValueError(f"Error: Could not read data file - {e}")
    
    def save_all(self, expenses: List[Expense]):
        """
        Save all expenses to file.
        
        Args:
            expenses: List of Expense objects to save
        """
        try:
            data = {
                "version": 1,
                "expenses": [exp.to_dict() for exp in expenses]
            }
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(expenses)} expenses to file")
        except Exception as e:
            logger.error(f"Failed to save expenses: {e}")
            raise ValueError(f"Error: Could not write to data file - {e}")
    
    def add(self, expense: Expense):
        """
        Add a new expense to storage.
        
        Args:
            expense: Expense object to add
        """
        expenses = self.load_all()
        expenses.append(expense)
        self.save_all(expenses)
        logger.info(f"Added expense: {expense.id}")
    
    def delete(self, expense_id: str) -> bool:
        """
        Delete an expense by ID.
        
        Args:
            expense_id: ID of expense to delete
            
        Returns:
            True if deleted, False if not found
        """
        expenses = self.load_all()
        initial_count = len(expenses)
        expenses = [exp for exp in expenses if exp.id != expense_id]
        
        if len(expenses) < initial_count:
            self.save_all(expenses)
            logger.info(f"Deleted expense: {expense_id}")
            return True
        return False
    
    def update(self, expense_id: str, updates: dict) -> Optional[Expense]:
        """
        Update an expense by ID.
        
        Args:
            expense_id: ID of expense to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated Expense object or None if not found
        """
        expenses = self.load_all()
        
        for i, exp in enumerate(expenses):
            if exp.id == expense_id:
                # Update fields
                exp_dict = exp.to_dict()
                exp_dict.update(updates)
                expenses[i] = Expense.from_dict(exp_dict)
                self.save_all(expenses)
                logger.info(f"Updated expense: {expense_id}")
                return expenses[i]
        
        return None