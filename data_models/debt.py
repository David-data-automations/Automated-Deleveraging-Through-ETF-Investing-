"""
Debt Data Model

Defines the structure for debt instruments and collections.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import date


class DebtType(Enum):
    """Type of debt instrument."""
    CREDIT_CARD = "credit_card"
    PERSONAL_LOAN = "personal_loan"
    STUDENT_LOAN = "student_loan"
    AUTO_LOAN = "auto_loan"
    MORTGAGE = "mortgage"
    MEDICAL = "medical"
    OTHER = "other"


@dataclass
class Debt:
    """Represents a single debt obligation."""
    name: str
    debt_type: DebtType
    current_balance: float
    annual_interest_rate: float  # As decimal (e.g., 0.18 for 18%)
    minimum_payment: float  # Monthly minimum payment
    due_day: int = 1  # Day of month payment is due (1-31)
    
    def monthly_interest_rate(self) -> float:
        """Calculate monthly interest rate from annual rate."""
        return self.annual_interest_rate / 12
    
    def interest_this_month(self) -> float:
        """Calculate interest accrued this month on current balance."""
        return self.current_balance * self.monthly_interest_rate()
    
    def principal_in_minimum(self) -> float:
        """Calculate how much of minimum payment goes to principal."""
        interest = self.interest_this_month()
        return max(0, self.minimum_payment - interest)
    
    def months_to_payoff_minimum_only(self) -> Optional[float]:
        """
        Calculate months to pay off debt with minimum payments only.
        
        Returns None if debt won't be paid off (minimum < interest).
        """
        if self.current_balance <= 0:
            return 0
        
        if self.minimum_payment <= self.interest_this_month():
            return None  # Will never pay off
        
        # Use amortization formula
        r = self.monthly_interest_rate()
        P = self.current_balance
        M = self.minimum_payment
        
        if r == 0:
            return P / M
        
        # n = -log(1 - rP/M) / log(1 + r)
        import math
        try:
            months = -math.log(1 - r * P / M) / math.log(1 + r)
            return months
        except (ValueError, ZeroDivisionError):
            return None
    
    def total_interest_if_minimum_only(self) -> Optional[float]:
        """
        Calculate total interest paid if only making minimum payments.
        
        Returns None if debt won't be paid off.
        """
        months = self.months_to_payoff_minimum_only()
        if months is None:
            return None
        
        total_paid = self.minimum_payment * months
        total_interest = total_paid - self.current_balance
        return max(0, total_interest)
    
    def validate(self) -> List[str]:
        """
        Validate debt data and return list of warnings/errors.
        
        Returns:
            List of validation messages (empty if all valid)
        """
        warnings = []
        
        if self.current_balance < 0:
            warnings.append(f"{self.name}: Balance cannot be negative")
        
        if self.annual_interest_rate < 0:
            warnings.append(f"{self.name}: Interest rate cannot be negative")
        
        if self.annual_interest_rate > 1.0:  # > 100% APR
            warnings.append(f"{self.name}: WARNING: Interest rate exceeds 100% APR")
        
        if self.minimum_payment < 0:
            warnings.append(f"{self.name}: Minimum payment cannot be negative")
        
        if self.current_balance > 0 and self.minimum_payment <= self.interest_this_month():
            warnings.append(
                f"{self.name}: CRITICAL: Minimum payment (${self.minimum_payment:.2f}) "
                f"does not cover monthly interest (${self.interest_this_month():.2f}). "
                f"Debt will grow indefinitely."
            )
        
        if self.due_day < 1 or self.due_day > 31:
            warnings.append(f"{self.name}: Due day must be between 1 and 31")
        
        return warnings


@dataclass
class DebtPortfolio:
    """Collection of all user debts."""
    debts: List[Debt] = field(default_factory=list)
    
    def total_balance(self) -> float:
        """Calculate total outstanding balance across all debts."""
        return sum(debt.current_balance for debt in self.debts)
    
    def total_minimum_payments(self) -> float:
        """Calculate total monthly minimum payments."""
        return sum(debt.minimum_payment for debt in self.debts)
    
    def weighted_average_interest_rate(self) -> float:
        """
        Calculate weighted average interest rate across all debts.
        
        Weighted by current balance.
        """
        total_balance = self.total_balance()
        if total_balance == 0:
            return 0.0
        
        weighted_sum = sum(
            debt.current_balance * debt.annual_interest_rate 
            for debt in self.debts
        )
        return weighted_sum / total_balance
    
    def highest_interest_debt(self) -> Optional[Debt]:
        """Return the debt with the highest interest rate."""
        if not self.debts:
            return None
        return max(self.debts, key=lambda d: d.annual_interest_rate)
    
    def smallest_balance_debt(self) -> Optional[Debt]:
        """Return the debt with the smallest balance."""
        if not self.debts:
            return None
        return min(self.debts, key=lambda d: d.current_balance)
    
    def total_monthly_interest(self) -> float:
        """Calculate total interest accruing across all debts this month."""
        return sum(debt.interest_this_month() for debt in self.debts)
    
    def has_high_interest_debt(self, threshold: float = 0.20) -> bool:
        """
        Check if any debt has interest rate above threshold.
        
        Args:
            threshold: Interest rate threshold (default 20% = 0.20)
        """
        return any(debt.annual_interest_rate > threshold for debt in self.debts)
    
    def validate(self) -> List[str]:
        """
        Validate all debts and return combined warnings/errors.
        
        Returns:
            List of validation messages (empty if all valid)
        """
        warnings = []
        
        if not self.debts:
            warnings.append("No debts defined")
        
        for debt in self.debts:
            warnings.extend(debt.validate())
        
        return warnings
