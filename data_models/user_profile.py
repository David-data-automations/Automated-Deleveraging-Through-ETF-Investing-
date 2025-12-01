"""
User Profile Data Model

Defines the structure for user financial information including income,
expenses, savings, risk tolerance, and time horizon.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class RiskTolerance(Enum):
    """User's risk tolerance level for investment decisions."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class PayFrequency(Enum):
    """Frequency of income payments."""
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    SEMI_MONTHLY = "semi_monthly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"


@dataclass
class IncomeStream:
    """Represents a single income source."""
    name: str
    amount: float  # Amount per payment period
    frequency: PayFrequency
    
    def monthly_amount(self) -> float:
        """Convert income to monthly equivalent."""
        multipliers = {
            PayFrequency.WEEKLY: 52 / 12,
            PayFrequency.BI_WEEKLY: 26 / 12,
            PayFrequency.SEMI_MONTHLY: 2,
            PayFrequency.MONTHLY: 1,
            PayFrequency.ANNUALLY: 1 / 12,
        }
        return self.amount * multipliers[self.frequency]


@dataclass
class Expense:
    """Represents a recurring expense."""
    name: str
    amount: float  # Monthly amount
    is_essential: bool = True  # True for fixed/essential, False for variable/discretionary


@dataclass
class UserProfile:
    """Complete user financial profile."""
    # Income
    income_streams: List[IncomeStream] = field(default_factory=list)
    
    # Expenses
    expenses: List[Expense] = field(default_factory=list)
    
    # Savings & Investments
    current_savings: float = 0.0
    current_investments: float = 0.0
    
    # Risk & Time
    risk_tolerance: RiskTolerance = RiskTolerance.CONSERVATIVE
    time_horizon_months: int = 60  # Default 5 years
    
    # Emergency fund target (in months of expenses)
    emergency_fund_months: float = 3.0
    
    def total_monthly_income(self) -> float:
        """Calculate total monthly income from all streams."""
        return sum(stream.monthly_amount() for stream in self.income_streams)
    
    def total_monthly_expenses(self) -> float:
        """Calculate total monthly expenses."""
        return sum(expense.amount for expense in self.expenses)
    
    def essential_monthly_expenses(self) -> float:
        """Calculate only essential monthly expenses."""
        return sum(expense.amount for expense in self.expenses if expense.is_essential)
    
    def emergency_fund_target(self) -> float:
        """Calculate target emergency fund amount."""
        return self.essential_monthly_expenses() * self.emergency_fund_months
    
    def has_adequate_emergency_fund(self) -> bool:
        """Check if user has adequate emergency savings."""
        return self.current_savings >= self.emergency_fund_target()
    
    def validate(self) -> List[str]:
        """
        Validate user profile and return list of warnings/errors.
        
        Returns:
            List of validation messages (empty if all valid)
        """
        warnings = []
        
        if not self.income_streams:
            warnings.append("No income streams defined")
        
        if self.total_monthly_income() <= 0:
            warnings.append("Total monthly income must be positive")
        
        if self.total_monthly_expenses() < 0:
            warnings.append("Total monthly expenses cannot be negative")
        
        if self.current_savings < 0:
            warnings.append("Current savings cannot be negative")
        
        if self.current_investments < 0:
            warnings.append("Current investments cannot be negative")
        
        if self.time_horizon_months <= 0:
            warnings.append("Time horizon must be positive")
        
        if self.emergency_fund_months < 0:
            warnings.append("Emergency fund months cannot be negative")
        
        # Check for negative cashflow
        if self.total_monthly_income() < self.total_monthly_expenses():
            warnings.append("WARNING: Monthly expenses exceed income (negative cashflow)")
        
        # Check for inadequate emergency fund
        if not self.has_adequate_emergency_fund():
            warnings.append(
                f"WARNING: Emergency fund (${self.current_savings:,.2f}) is below "
                f"recommended target (${self.emergency_fund_target():,.2f})"
            )
        
        return warnings
