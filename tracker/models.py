"""
Data models for the expense tracker.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Expense:
    """
    Represents a single expense entry.
    
    Attributes:
        id: Unique identifier (format: EXP-YYYYMMDD-NNNN)
        date: Date of expense (YYYY-MM-DD format)
        category: Category of expense (e.g., food, transport, rent)
        amount: Amount spent (must be > 0)
        currency: Currency code (default: BDT)
        note: Optional note/description
        created_at: Timestamp when expense was created
    """
    id: str
    date: str
    category: str
    amount: float
    currency: str = "BDT"
    note: str = ""
    created_at: str = ""
    
    def to_dict(self) -> dict:
        """Convert expense to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Expense':
        """Create expense from dictionary."""
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.id} | {self.date} | {self.category} | {self.amount:.2f} {self.currency} | {self.note}"