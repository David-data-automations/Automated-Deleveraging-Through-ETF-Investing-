"""
Plan Data Model

Defines the structure for debt payoff plans and recommendations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class PayoffStrategy(Enum):
    """Strategy for prioritizing debt payoff."""
    AVALANCHE = "avalanche"  # Highest interest rate first
    SNOWBALL = "snowball"    # Smallest balance first
    HYBRID = "hybrid"        # Combination approach


@dataclass
class MonthlyPayment:
    """Represents a payment allocation for a specific debt in a given month."""
    debt_name: str
    total_payment: float
    principal: float
    interest: float
    remaining_balance: float


@dataclass
class MonthlyPlan:
    """Complete plan for a single month."""
    month: int  # Month number (1-indexed)
    payments: List[MonthlyPayment] = field(default_factory=list)
    etf_contribution: float = 0.0
    total_debt_payment: float = 0.0
    total_remaining_debt: float = 0.0
    
    def total_allocated(self) -> float:
        """Total amount allocated this month (debt + ETF)."""
        return self.total_debt_payment + self.etf_contribution


@dataclass
class ETFAllocation:
    """ETF investment allocation recommendation."""
    category: str  # e.g., "Total Market", "S&P 500", "Bond Index"
    percentage: float  # Percentage of ETF contribution
    example_ticker: str  # Example ticker symbol (for reference only)
    description: str


@dataclass
class DebtPayoffPlan:
    """Complete debt payoff and investment plan."""
    # Strategy
    strategy: PayoffStrategy
    
    # Allocations
    monthly_surplus: float  # Available after income - expenses - minimums
    debt_allocation_percentage: float  # % of surplus to debt
    etf_allocation_percentage: float   # % of surplus to ETF
    
    monthly_extra_debt_payment: float  # Extra payment beyond minimums
    monthly_etf_contribution: float    # Monthly ETF investment
    
    # ETF recommendations
    etf_allocations: List[ETFAllocation] = field(default_factory=list)
    
    # Timeline
    estimated_months_to_debt_free: Optional[float] = None
    monthly_plans: List[MonthlyPlan] = field(default_factory=list)
    
    # Summary metrics
    total_interest_paid: float = 0.0
    total_interest_saved: float = 0.0  # vs minimum-only approach
    estimated_etf_value_low: float = 0.0
    estimated_etf_value_medium: float = 0.0
    estimated_etf_value_high: float = 0.0
    
    # Warnings and recommendations
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ScenarioComparison:
    """Comparison between different planning scenarios."""
    scenario_name: str
    
    # Debt metrics
    months_to_debt_free: Optional[float]
    total_interest_paid: float
    total_debt_payments: float
    
    # Investment metrics
    total_etf_contributions: float
    estimated_etf_value_low: float
    estimated_etf_value_medium: float
    estimated_etf_value_high: float
    
    # Net worth projection
    net_worth_at_end_low: float
    net_worth_at_end_medium: float
    net_worth_at_end_high: float
    
    description: str = ""


@dataclass
class PlanOutput:
    """
    Complete output from the planning engine.
    
    Includes the recommended plan, alternative scenarios, and explanations.
    """
    # Recommended plan
    recommended_plan: DebtPayoffPlan
    
    # Alternative scenarios for comparison
    debt_only_scenario: Optional[ScenarioComparison] = None
    balanced_scenario: Optional[ScenarioComparison] = None
    minimum_only_scenario: Optional[ScenarioComparison] = None
    
    # Narrative explanations
    executive_summary: str = ""
    detailed_explanation: str = ""
    tradeoff_analysis: str = ""
    action_steps: List[str] = field(default_factory=list)
    
    # Disclaimers (always included)
    disclaimer: str = (
        "IMPORTANT DISCLAIMER: This tool provides educational planning estimates only "
        "and is not financial, investment, tax, or legal advice. All projections are "
        "hypothetical and not guaranteed. Actual results may vary significantly. "
        "Consider consulting a qualified financial professional before making financial decisions."
    )
    
    def get_comparison_table(self) -> List[Dict[str, any]]:
        """
        Generate a comparison table of all scenarios.
        
        Returns:
            List of dictionaries suitable for tabular display
        """
        scenarios = []
        
        if self.minimum_only_scenario:
            scenarios.append(self.minimum_only_scenario)
        if self.debt_only_scenario:
            scenarios.append(self.debt_only_scenario)
        if self.balanced_scenario:
            scenarios.append(self.balanced_scenario)
        
        table = []
        for scenario in scenarios:
            table.append({
                'Scenario': scenario.scenario_name,
                'Months to Debt-Free': (
                    f"{scenario.months_to_debt_free:.0f}" 
                    if scenario.months_to_debt_free else "N/A"
                ),
                'Total Interest Paid': f"${scenario.total_interest_paid:,.2f}",
                'Total ETF Invested': f"${scenario.total_etf_contributions:,.2f}",
                'Est. ETF Value (Medium)': f"${scenario.estimated_etf_value_medium:,.2f}",
                'Est. Net Worth (Medium)': f"${scenario.net_worth_at_end_medium:,.2f}",
            })
        
        return table
