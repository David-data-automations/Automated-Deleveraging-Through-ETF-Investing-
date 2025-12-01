"""
Cashflow Engine

Handles all income, expense, and debt payment calculations.
Computes available surplus and validates financial viability.
"""

from typing import Tuple, List, Optional
from data_models import UserProfile, DebtPortfolio, Debt


class CashflowAnalyzer:
    """Analyzes user cashflow and debt obligations."""
    
    def __init__(self, profile: UserProfile, debts: DebtPortfolio):
        """
        Initialize cashflow analyzer.
        
        Args:
            profile: User financial profile
            debts: User debt portfolio
        """
        self.profile = profile
        self.debts = debts
    
    def monthly_gross_income(self) -> float:
        """Calculate total monthly gross income."""
        return self.profile.total_monthly_income()
    
    def monthly_total_expenses(self) -> float:
        """Calculate total monthly expenses (essential + discretionary)."""
        return self.profile.total_monthly_expenses()
    
    def monthly_essential_expenses(self) -> float:
        """Calculate only essential monthly expenses."""
        return self.profile.essential_monthly_expenses()
    
    def monthly_minimum_debt_payments(self) -> float:
        """Calculate total monthly minimum debt payments."""
        return self.debts.total_minimum_payments()
    
    def monthly_obligations(self) -> float:
        """
        Calculate total monthly obligations.
        
        Includes all expenses plus minimum debt payments.
        """
        return self.monthly_total_expenses() + self.monthly_minimum_debt_payments()
    
    def monthly_essential_obligations(self) -> float:
        """
        Calculate essential monthly obligations only.
        
        Includes essential expenses plus minimum debt payments.
        """
        return self.monthly_essential_expenses() + self.monthly_minimum_debt_payments()
    
    def monthly_surplus(self) -> float:
        """
        Calculate monthly surplus after all obligations.
        
        This is the amount available for extra debt payments and/or investing.
        """
        return self.monthly_gross_income() - self.monthly_obligations()
    
    def monthly_conservative_surplus(self) -> float:
        """
        Calculate conservative monthly surplus.
        
        Uses essential expenses only, providing a more conservative estimate.
        """
        return self.monthly_gross_income() - self.monthly_essential_obligations()
    
    def has_positive_cashflow(self) -> bool:
        """Check if user has positive cashflow."""
        return self.monthly_surplus() > 0
    
    def cashflow_health_score(self) -> str:
        """
        Assess overall cashflow health.
        
        Returns:
            Health rating: "critical", "poor", "fair", "good", or "excellent"
        """
        surplus = self.monthly_surplus()
        income = self.monthly_gross_income()
        
        if surplus <= 0:
            return "critical"
        
        surplus_ratio = surplus / income if income > 0 else 0
        
        if surplus_ratio < 0.05:  # Less than 5%
            return "poor"
        elif surplus_ratio < 0.15:  # 5-15%
            return "fair"
        elif surplus_ratio < 0.25:  # 15-25%
            return "good"
        else:  # 25%+
            return "excellent"
    
    def debt_to_income_ratio(self) -> float:
        """
        Calculate debt-to-income ratio.
        
        Returns:
            Ratio of total debt balance to annual income
        """
        annual_income = self.monthly_gross_income() * 12
        if annual_income == 0:
            return float('inf')
        return self.debts.total_balance() / annual_income
    
    def debt_service_ratio(self) -> float:
        """
        Calculate debt service ratio.
        
        Returns:
            Ratio of monthly debt payments to monthly gross income
        """
        income = self.monthly_gross_income()
        if income == 0:
            return float('inf')
        return self.monthly_minimum_debt_payments() / income
    
    def get_red_flags(self) -> List[str]:
        """
        Identify financial red flags.
        
        Returns:
            List of warning messages about concerning financial conditions
        """
        flags = []
        
        # Negative cashflow
        if not self.has_positive_cashflow():
            flags.append(
                "CRITICAL: Negative monthly cashflow. "
                "Expenses and debt payments exceed income."
            )
        
        # Very low surplus
        surplus = self.monthly_surplus()
        if 0 < surplus < 100:
            flags.append(
                f"WARNING: Very low monthly surplus (${surplus:.2f}). "
                "Limited room for extra payments or emergencies."
            )
        
        # High debt-to-income ratio
        dti = self.debt_to_income_ratio()
        if dti > 2.0:
            flags.append(
                f"WARNING: High debt-to-income ratio ({dti:.1f}x annual income). "
                "Consider debt consolidation or credit counseling."
            )
        
        # High debt service ratio
        dsr = self.debt_service_ratio()
        if dsr > 0.43:  # 43% is common DTI threshold for mortgages
            flags.append(
                f"WARNING: High debt service ratio ({dsr:.1%} of income). "
                "Debt payments consume a large portion of income."
            )
        
        # Inadequate emergency fund
        if not self.profile.has_adequate_emergency_fund():
            flags.append(
                f"WARNING: Emergency fund (${self.profile.current_savings:,.2f}) "
                f"below recommended {self.profile.emergency_fund_months} months "
                f"of expenses (${self.profile.emergency_fund_target():,.2f})."
            )
        
        # High-interest debt
        if self.debts.has_high_interest_debt(threshold=0.20):
            highest = self.debts.highest_interest_debt()
            if highest:
                flags.append(
                    f"WARNING: High-interest debt detected. "
                    f"{highest.name} has {highest.annual_interest_rate:.1%} APR. "
                    "Prioritize paying this down."
                )
        
        # Debts that won't pay off with minimums
        for debt in self.debts.debts:
            if debt.current_balance > 0 and debt.minimum_payment <= debt.interest_this_month():
                flags.append(
                    f"CRITICAL: {debt.name} minimum payment does not cover interest. "
                    "Balance will grow indefinitely. Increase payments immediately."
                )
        
        return flags
    
    def calculate_safe_surplus(self, safety_margin: float = 0.1) -> float:
        """
        Calculate safe monthly surplus with safety margin.
        
        Args:
            safety_margin: Percentage to hold back as buffer (default 10%)
        
        Returns:
            Conservative surplus amount safe to allocate
        """
        surplus = self.monthly_surplus()
        if surplus <= 0:
            return 0.0
        
        safe_surplus = surplus * (1 - safety_margin)
        return max(0, safe_surplus)
    
    def get_cashflow_summary(self) -> dict:
        """
        Generate comprehensive cashflow summary.
        
        Returns:
            Dictionary with all key cashflow metrics
        """
        return {
            'monthly_income': self.monthly_gross_income(),
            'monthly_expenses': self.monthly_total_expenses(),
            'monthly_debt_minimums': self.monthly_minimum_debt_payments(),
            'monthly_obligations': self.monthly_obligations(),
            'monthly_surplus': self.monthly_surplus(),
            'safe_surplus': self.calculate_safe_surplus(),
            'cashflow_health': self.cashflow_health_score(),
            'debt_to_income_ratio': self.debt_to_income_ratio(),
            'debt_service_ratio': self.debt_service_ratio(),
            'emergency_fund_status': {
                'current': self.profile.current_savings,
                'target': self.profile.emergency_fund_target(),
                'adequate': self.profile.has_adequate_emergency_fund(),
            },
            'red_flags': self.get_red_flags(),
        }


def calculate_amortization_schedule(
    principal: float,
    annual_rate: float,
    monthly_payment: float,
    max_months: int = 600
) -> List[Tuple[int, float, float, float]]:
    """
    Calculate amortization schedule for a debt.
    
    Args:
        principal: Initial loan balance
        annual_rate: Annual interest rate (as decimal)
        monthly_payment: Fixed monthly payment amount
        max_months: Maximum months to calculate (default 600 = 50 years)
    
    Returns:
        List of tuples: (month, payment, interest, principal, remaining_balance)
    """
    schedule = []
    balance = principal
    monthly_rate = annual_rate / 12
    
    for month in range(1, max_months + 1):
        if balance <= 0:
            break
        
        interest = balance * monthly_rate
        principal_payment = min(monthly_payment - interest, balance)
        
        # Handle case where payment doesn't cover interest
        if principal_payment <= 0:
            # Debt is growing, stop calculation
            break
        
        balance -= principal_payment
        
        schedule.append((
            month,
            min(monthly_payment, interest + balance + principal_payment),
            interest,
            principal_payment,
            max(0, balance)
        ))
    
    return schedule


def calculate_total_interest(
    principal: float,
    annual_rate: float,
    monthly_payment: float
) -> Optional[float]:
    """
    Calculate total interest paid over life of debt.
    
    Args:
        principal: Initial loan balance
        annual_rate: Annual interest rate (as decimal)
        monthly_payment: Fixed monthly payment amount
    
    Returns:
        Total interest paid, or None if debt won't pay off
    """
    schedule = calculate_amortization_schedule(principal, annual_rate, monthly_payment)
    
    if not schedule:
        return None
    
    # Check if debt was fully paid off
    final_balance = schedule[-1][4]
    if final_balance > 0.01:  # Allow for small rounding errors
        return None
    
    total_interest = sum(payment[2] for payment in schedule)
    return total_interest
