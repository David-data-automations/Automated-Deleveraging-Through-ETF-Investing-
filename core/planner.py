"""
Main Planner

Orchestrates all components to generate a complete debt deleveraging plan.
"""

from typing import Optional
from data_models import (
    UserProfile, DebtPortfolio, PayoffStrategy,
    DebtPayoffPlan, PlanOutput
)
from core.cashflow import CashflowAnalyzer
from core.etf_allocation import ETFAllocationEngine
from core.simulation import SimulationEngine
from core.explanations import NarrativeGenerator


class DeleveragingPlanner:
    """Main orchestrator for debt deleveraging planning."""
    
    def __init__(
        self,
        profile: UserProfile,
        debts: DebtPortfolio,
        strategy: PayoffStrategy = PayoffStrategy.AVALANCHE
    ):
        """
        Initialize the planner.
        
        Args:
            profile: User financial profile
            debts: User debt portfolio
            strategy: Preferred payoff strategy (default: avalanche)
        """
        self.profile = profile
        self.debts = debts
        self.strategy = strategy
        
        # Initialize engines
        self.cashflow = CashflowAnalyzer(profile, debts)
        self.etf_engine = ETFAllocationEngine(profile, debts)
        self.simulation = SimulationEngine(debts)
    
    def validate_inputs(self) -> tuple[bool, list[str]]:
        """
        Validate all inputs before planning.
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Validate profile
        warnings.extend(self.profile.validate())
        
        # Validate debts
        warnings.extend(self.debts.validate())
        
        # Get cashflow red flags
        warnings.extend(self.cashflow.get_red_flags())
        
        # Critical errors that prevent planning
        critical_errors = [
            w for w in warnings 
            if w.startswith("CRITICAL") or "cannot be negative" in w
        ]
        
        is_valid = len(critical_errors) == 0
        
        return is_valid, warnings
    
    def create_plan(
        self,
        use_safe_surplus: bool = True,
        custom_debt_percentage: Optional[float] = None,
        custom_etf_percentage: Optional[float] = None
    ) -> PlanOutput:
        """
        Create a complete debt deleveraging plan.
        
        Args:
            use_safe_surplus: Use conservative surplus with safety margin
            custom_debt_percentage: Override debt allocation percentage (0.0-1.0)
            custom_etf_percentage: Override ETF allocation percentage (0.0-1.0)
        
        Returns:
            Complete PlanOutput with recommendations and analysis
        """
        # Validate inputs
        is_valid, warnings = self.validate_inputs()
        
        if not is_valid:
            # Return a plan with warnings but no recommendations
            empty_plan = DebtPayoffPlan(
                strategy=self.strategy,
                monthly_surplus=0.0,
                debt_allocation_percentage=1.0,
                etf_allocation_percentage=0.0,
                monthly_extra_debt_payment=0.0,
                monthly_etf_contribution=0.0,
                warnings=warnings
            )
            
            return PlanOutput(
                recommended_plan=empty_plan,
                executive_summary="Unable to create plan due to critical errors. Please review warnings.",
                detailed_explanation="",
                tradeoff_analysis="",
                action_steps=["Address critical errors before proceeding with planning."]
            )
        
        # Calculate surplus
        if use_safe_surplus:
            monthly_surplus = self.cashflow.calculate_safe_surplus()
        else:
            monthly_surplus = self.cashflow.monthly_surplus()
        
        # Determine allocation
        if custom_debt_percentage is not None and custom_etf_percentage is not None:
            debt_pct = custom_debt_percentage
            etf_pct = custom_etf_percentage
            allocation_reasoning = ["Using custom allocation percentages."]
            
            # Validate custom allocation
            validation_warnings = self.etf_engine.validate_allocation(debt_pct, etf_pct)
            warnings.extend(validation_warnings)
        else:
            debt_pct, etf_pct, allocation_reasoning = \
                self.etf_engine.calculate_allocation_split(monthly_surplus)
        
        # Calculate monthly amounts
        monthly_extra_debt = monthly_surplus * debt_pct
        monthly_etf = monthly_surplus * etf_pct
        
        # Get ETF recommendations
        etf_allocations = self.etf_engine.get_etf_recommendations()
        
        # Get expected returns
        return_low, return_med, return_high = self.etf_engine.get_expected_returns()
        
        # Simulate the recommended plan
        recommended_results = self.simulation.simulate_combined_scenario(
            monthly_extra_debt=monthly_extra_debt,
            monthly_etf=monthly_etf,
            strategy=self.strategy,
            annual_return_low=return_low,
            annual_return_med=return_med,
            annual_return_high=return_high,
            initial_etf_balance=self.profile.current_investments
        )
        
        # Calculate interest saved
        from core.payoff_strategies import PayoffStrategyEngine
        interest_with_extra, interest_minimum_only = \
            PayoffStrategyEngine.calculate_interest_saved(
                self.debts.debts,
                monthly_extra_debt,
                self.strategy
            )
        interest_saved = interest_minimum_only - interest_with_extra
        
        # Create recommended plan
        recommended_plan = DebtPayoffPlan(
            strategy=self.strategy,
            monthly_surplus=monthly_surplus,
            debt_allocation_percentage=debt_pct,
            etf_allocation_percentage=etf_pct,
            monthly_extra_debt_payment=monthly_extra_debt,
            monthly_etf_contribution=monthly_etf,
            etf_allocations=etf_allocations,
            estimated_months_to_debt_free=recommended_results['months_to_debt_free'],
            total_interest_paid=recommended_results['total_interest_paid'],
            total_interest_saved=interest_saved,
            estimated_etf_value_low=recommended_results['final_etf_value_low'],
            estimated_etf_value_medium=recommended_results['final_etf_value_medium'],
            estimated_etf_value_high=recommended_results['final_etf_value_high'],
            warnings=warnings,
            recommendations=allocation_reasoning
        )
        
        # Generate comparison scenarios
        minimum_only, debt_only, balanced = self.simulation.compare_scenarios(
            monthly_surplus=monthly_surplus,
            strategy=self.strategy,
            annual_return_low=return_low,
            annual_return_med=return_med,
            annual_return_high=return_high,
            initial_etf_balance=self.profile.current_investments
        )
        
        # Generate complete output with narratives
        output = NarrativeGenerator.generate_complete_output(
            plan=recommended_plan,
            profile=self.profile,
            debts=self.debts,
            cashflow=self.cashflow,
            minimum_only=minimum_only,
            debt_only=debt_only,
            balanced=balanced
        )
        
        return output
    
    def get_cashflow_summary(self) -> dict:
        """Get comprehensive cashflow summary."""
        return self.cashflow.get_cashflow_summary()
    
    def get_debt_summary(self) -> dict:
        """Get comprehensive debt summary."""
        return {
            'total_balance': self.debts.total_balance(),
            'total_minimum_payments': self.debts.total_minimum_payments(),
            'weighted_avg_rate': self.debts.weighted_average_interest_rate(),
            'total_monthly_interest': self.debts.total_monthly_interest(),
            'num_debts': len(self.debts.debts),
            'has_high_interest': self.debts.has_high_interest_debt(),
            'debts': [
                {
                    'name': debt.name,
                    'type': debt.debt_type.value,
                    'balance': debt.current_balance,
                    'rate': debt.annual_interest_rate,
                    'minimum': debt.minimum_payment,
                    'monthly_interest': debt.interest_this_month(),
                }
                for debt in self.debts.debts
            ]
        }
