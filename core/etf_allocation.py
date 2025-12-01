"""
ETF Allocation Engine

Determines appropriate allocation between debt payoff and ETF investing
based on user profile, debt characteristics, and risk tolerance.
"""

from typing import Tuple, List
from data_models import (
    UserProfile, DebtPortfolio, RiskTolerance, ETFAllocation
)


class ETFAllocationEngine:
    """Manages allocation between debt payoff and ETF investing."""
    
    # Configuration parameters (can be tuned)
    HIGH_INTEREST_THRESHOLD = 0.20  # 20% APR
    VERY_HIGH_INTEREST_THRESHOLD = 0.15  # 15% APR
    MODERATE_INTEREST_THRESHOLD = 0.10  # 10% APR
    
    # Conservative expected returns (annual)
    CONSERVATIVE_MARKET_RETURN = 0.06  # 6%
    MODERATE_MARKET_RETURN = 0.08      # 8%
    AGGRESSIVE_MARKET_RETURN = 0.10    # 10%
    
    def __init__(self, profile: UserProfile, debts: DebtPortfolio):
        """
        Initialize ETF allocation engine.
        
        Args:
            profile: User financial profile
            debts: User debt portfolio
        """
        self.profile = profile
        self.debts = debts
    
    def calculate_allocation_split(
        self,
        monthly_surplus: float
    ) -> Tuple[float, float, List[str]]:
        """
        Calculate recommended split between debt and ETF.
        
        Args:
            monthly_surplus: Available monthly surplus
        
        Returns:
            Tuple of:
            - Percentage to debt (0.0 to 1.0)
            - Percentage to ETF (0.0 to 1.0)
            - List of reasoning/explanation strings
        """
        reasoning = []
        
        # Default: no investing if no surplus
        if monthly_surplus <= 0:
            reasoning.append("No surplus available for extra payments or investing.")
            return 1.0, 0.0, reasoning
        
        # Rule 1: No emergency fund = 100% to debt (build emergency fund first)
        if not self.profile.has_adequate_emergency_fund():
            reasoning.append(
                "Emergency fund is below recommended level. "
                "Prioritizing debt payoff over investing. "
                "Consider building emergency savings alongside debt reduction."
            )
            return 1.0, 0.0, reasoning
        
        # Rule 2: Very high interest debt (>20%) = 100% to debt
        if self.debts.has_high_interest_debt(self.HIGH_INTEREST_THRESHOLD):
            highest = self.debts.highest_interest_debt()
            reasoning.append(
                f"Very high-interest debt detected ({highest.name} at "
                f"{highest.annual_interest_rate:.1%} APR). "
                f"Paying down this debt provides guaranteed return exceeding "
                f"typical market returns. Allocating 100% to debt payoff."
            )
            return 1.0, 0.0, reasoning
        
        # Rule 3: High interest debt (15-20%) = mostly debt, minimal ETF
        if self.debts.has_high_interest_debt(self.VERY_HIGH_INTEREST_THRESHOLD):
            highest = self.debts.highest_interest_debt()
            reasoning.append(
                f"High-interest debt detected ({highest.name} at "
                f"{highest.annual_interest_rate:.1%} APR). "
                f"Strongly prioritizing debt payoff with minimal ETF allocation."
            )
            
            if self.profile.risk_tolerance == RiskTolerance.AGGRESSIVE:
                return 0.85, 0.15, reasoning
            else:
                return 0.90, 0.10, reasoning
        
        # Rule 4: Moderate interest debt (10-15%) = balanced approach
        if self.debts.has_high_interest_debt(self.MODERATE_INTEREST_THRESHOLD):
            avg_rate = self.debts.weighted_average_interest_rate()
            reasoning.append(
                f"Moderate-interest debt (weighted average {avg_rate:.1%} APR). "
                f"Using balanced approach between debt payoff and investing."
            )
            
            if self.profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
                return 0.80, 0.20, reasoning
            elif self.profile.risk_tolerance == RiskTolerance.MODERATE:
                return 0.70, 0.30, reasoning
            else:  # AGGRESSIVE
                return 0.60, 0.40, reasoning
        
        # Rule 5: Low interest debt (<10%) = favor investing more
        avg_rate = self.debts.weighted_average_interest_rate()
        reasoning.append(
            f"Low-interest debt (weighted average {avg_rate:.1%} APR). "
            f"Expected market returns may exceed debt interest. "
            f"Allocating more to ETF investing while maintaining debt payoff."
        )
        
        if self.profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            return 0.70, 0.30, reasoning
        elif self.profile.risk_tolerance == RiskTolerance.MODERATE:
            return 0.60, 0.40, reasoning
        else:  # AGGRESSIVE
            return 0.50, 0.50, reasoning
    
    def get_etf_recommendations(self) -> List[ETFAllocation]:
        """
        Get ETF allocation recommendations based on risk tolerance.
        
        Returns:
            List of recommended ETF allocations
        """
        if self.profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            return [
                ETFAllocation(
                    category="Bond Index",
                    percentage=0.50,
                    example_ticker="BND",
                    description="Broad U.S. investment-grade bonds for stability"
                ),
                ETFAllocation(
                    category="Total Market Index",
                    percentage=0.40,
                    example_ticker="VTI",
                    description="Broad U.S. stock market exposure"
                ),
                ETFAllocation(
                    category="International Bonds",
                    percentage=0.10,
                    example_ticker="BNDX",
                    description="International investment-grade bonds for diversification"
                ),
            ]
        
        elif self.profile.risk_tolerance == RiskTolerance.MODERATE:
            return [
                ETFAllocation(
                    category="Total Market Index",
                    percentage=0.50,
                    example_ticker="VTI",
                    description="Broad U.S. stock market exposure"
                ),
                ETFAllocation(
                    category="Bond Index",
                    percentage=0.30,
                    example_ticker="BND",
                    description="U.S. investment-grade bonds for stability"
                ),
                ETFAllocation(
                    category="International Stock Index",
                    percentage=0.20,
                    example_ticker="VXUS",
                    description="International stock market diversification"
                ),
            ]
        
        else:  # AGGRESSIVE
            return [
                ETFAllocation(
                    category="Total Market Index",
                    percentage=0.60,
                    example_ticker="VTI",
                    description="Broad U.S. stock market exposure"
                ),
                ETFAllocation(
                    category="International Stock Index",
                    percentage=0.25,
                    example_ticker="VXUS",
                    description="International stock market diversification"
                ),
                ETFAllocation(
                    category="Bond Index",
                    percentage=0.15,
                    example_ticker="BND",
                    description="U.S. investment-grade bonds for some stability"
                ),
            ]
    
    def get_expected_returns(self) -> Tuple[float, float, float]:
        """
        Get expected annual returns based on risk tolerance.
        
        Returns:
            Tuple of (low, medium, high) annual return estimates
        """
        if self.profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            return 0.03, 0.05, 0.07  # 3%, 5%, 7%
        elif self.profile.risk_tolerance == RiskTolerance.MODERATE:
            return 0.04, 0.07, 0.10  # 4%, 7%, 10%
        else:  # AGGRESSIVE
            return 0.05, 0.08, 0.12  # 5%, 8%, 12%
    
    def should_invest_vs_payoff(self) -> Tuple[bool, str]:
        """
        Determine if user should invest at all vs 100% debt payoff.
        
        Returns:
            Tuple of (should_invest, explanation)
        """
        # No emergency fund
        if not self.profile.has_adequate_emergency_fund():
            return False, (
                "Build adequate emergency fund before investing. "
                "Focus on debt payoff and emergency savings first."
            )
        
        # Very high interest debt
        if self.debts.has_high_interest_debt(self.HIGH_INTEREST_THRESHOLD):
            highest = self.debts.highest_interest_debt()
            return False, (
                f"High-interest debt ({highest.name} at {highest.annual_interest_rate:.1%}) "
                f"provides guaranteed return by paying it down that exceeds expected market returns. "
                f"Focus 100% on debt elimination."
            )
        
        # Otherwise, some investing is reasonable
        avg_rate = self.debts.weighted_average_interest_rate()
        expected_low, expected_med, expected_high = self.get_expected_returns()
        
        return True, (
            f"Debt interest rate ({avg_rate:.1%}) is moderate. "
            f"Expected market returns ({expected_med:.1%} medium estimate) "
            f"may provide comparable or better returns. "
            f"A balanced approach between debt payoff and investing is reasonable."
        )
    
    def validate_allocation(
        self,
        debt_percentage: float,
        etf_percentage: float
    ) -> List[str]:
        """
        Validate proposed allocation.
        
        Args:
            debt_percentage: Proposed debt allocation (0.0 to 1.0)
            etf_percentage: Proposed ETF allocation (0.0 to 1.0)
        
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        # Check percentages are valid
        if debt_percentage < 0 or debt_percentage > 1:
            warnings.append("Debt percentage must be between 0 and 1")
        
        if etf_percentage < 0 or etf_percentage > 1:
            warnings.append("ETF percentage must be between 0 and 1")
        
        # Check they sum to ~1.0
        total = debt_percentage + etf_percentage
        if abs(total - 1.0) > 0.01:
            warnings.append(
                f"Debt and ETF percentages must sum to 100% (currently {total*100:.1f}%)"
            )
        
        # Warn if investing with no emergency fund
        if etf_percentage > 0 and not self.profile.has_adequate_emergency_fund():
            warnings.append(
                "WARNING: Investing without adequate emergency fund is risky. "
                "Consider building emergency savings first."
            )
        
        # Warn if investing with very high interest debt
        if etf_percentage > 0.1 and self.debts.has_high_interest_debt(self.HIGH_INTEREST_THRESHOLD):
            warnings.append(
                "WARNING: Investing while carrying very high-interest debt "
                "may not be optimal. The guaranteed return from paying down "
                "debt likely exceeds expected market returns."
            )
        
        return warnings
