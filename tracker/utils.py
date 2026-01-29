from datetime import datetime

def generate_id(date: str) -> str:
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
