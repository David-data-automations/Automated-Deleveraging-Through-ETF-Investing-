"""
Data Models Package

Contains all data structures for the Debt Deleveraging Bot.
"""

from .user_profile import (
    UserProfile,
    IncomeStream,
    Expense,
    RiskTolerance,
    PayFrequency,
)

from .debt import (
    Debt,
    DebtPortfolio,
    DebtType,
)

from .plan import (
    DebtPayoffPlan,
    MonthlyPlan,
    MonthlyPayment,
    ETFAllocation,
    ScenarioComparison,
    PlanOutput,
    PayoffStrategy,
)

__all__ = [
    # User Profile
    'UserProfile',
    'IncomeStream',
    'Expense',
    'RiskTolerance',
    'PayFrequency',
    
    # Debt
    'Debt',
    'DebtPortfolio',
    'DebtType',
    
    # Plan
    'DebtPayoffPlan',
    'MonthlyPlan',
    'MonthlyPayment',
    'ETFAllocation',
    'ScenarioComparison',
    'PlanOutput',
    'PayoffStrategy',
]
