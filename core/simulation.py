"""
Simulation Engine

Simulates debt payoff and ETF growth over time under different scenarios.
"""

from typing import List, Tuple, Dict
from data_models import (
    Debt, DebtPortfolio, PayoffStrategy, ScenarioComparison
)
from core.payoff_strategies import PayoffStrategyEngine
import copy


class SimulationEngine:
    """Simulates financial outcomes over time."""
    
    def __init__(self, debts: DebtPortfolio):
        """
        Initialize simulation engine.
        
        Args:
            debts: User debt portfolio
        """
        self.debts = debts
    
    def simulate_etf_growth(
        self,
        monthly_contribution: float,
        annual_return: float,
        months: int,
        initial_balance: float = 0.0
    ) -> List[float]:
        """
        Simulate ETF portfolio growth over time.
        
        Args:
            monthly_contribution: Monthly investment amount
            annual_return: Expected annual return (as decimal)
            months: Number of months to simulate
            initial_balance: Starting portfolio balance
        
        Returns:
            List of portfolio values for each month
        """
        monthly_return = annual_return / 12
        balance = initial_balance
        values = []
        
        for month in range(months):
            # Add contribution
            balance += monthly_contribution
            
            # Apply return
            balance *= (1 + monthly_return)
            
            values.append(balance)
        
        return values
    
    def simulate_combined_scenario(
        self,
        monthly_extra_debt: float,
        monthly_etf: float,
        strategy: PayoffStrategy,
        annual_return_low: float,
        annual_return_med: float,
        annual_return_high: float,
        initial_etf_balance: float = 0.0,
        max_months: int = 600
    ) -> Dict:
        """
        Simulate combined debt payoff + ETF investing scenario.
        
        Args:
            monthly_extra_debt: Extra monthly payment to debt
            monthly_etf: Monthly ETF contribution
            strategy: Debt payoff strategy
            annual_return_low: Low annual return estimate
            annual_return_med: Medium annual return estimate
            annual_return_high: High annual return estimate
            initial_etf_balance: Starting ETF balance
            max_months: Maximum months to simulate
        
        Returns:
            Dictionary with simulation results
        """
        # Simulate debt payoff
        debt_snapshots, total_interest, months_to_debt_free = \
            PayoffStrategyEngine.simulate_payoff(
                self.debts.debts,
                monthly_extra_debt,
                strategy,
                max_months
            )
        
        # Determine simulation length
        sim_months = min(months_to_debt_free, max_months)
        
        # After debt is paid off, redirect debt payments to ETF
        monthly_etf_after_debt_free = monthly_etf + monthly_extra_debt + self.debts.total_minimum_payments()
        
        # Simulate ETF growth during debt payoff period
        etf_values_low = []
        etf_values_med = []
        etf_values_high = []
        
        balance_low = initial_etf_balance
        balance_med = initial_etf_balance
        balance_high = initial_etf_balance
        
        monthly_return_low = annual_return_low / 12
        monthly_return_med = annual_return_med / 12
        monthly_return_high = annual_return_high / 12
        
        for month in range(sim_months):
            # During debt payoff
            contribution = monthly_etf
            
            balance_low += contribution
            balance_low *= (1 + monthly_return_low)
            etf_values_low.append(balance_low)
            
            balance_med += contribution
            balance_med *= (1 + monthly_return_med)
            etf_values_med.append(balance_med)
            
            balance_high += contribution
            balance_high *= (1 + monthly_return_high)
            etf_values_high.append(balance_high)
        
        # Continue ETF growth after debt-free with increased contributions
        remaining_months = max_months - sim_months
        if remaining_months > 0:
            for month in range(remaining_months):
                contribution = monthly_etf_after_debt_free
                
                balance_low += contribution
                balance_low *= (1 + monthly_return_low)
                etf_values_low.append(balance_low)
                
                balance_med += contribution
                balance_med *= (1 + monthly_return_med)
                etf_values_med.append(balance_med)
                
                balance_high += contribution
                balance_high *= (1 + monthly_return_high)
                etf_values_high.append(balance_high)
        
        # Calculate total contributions
        total_etf_contributions = (monthly_etf * sim_months) + \
                                 (monthly_etf_after_debt_free * remaining_months)
        
        total_debt_payments = sum(
            snapshot['total_payment'] 
            for snapshot in debt_snapshots
        )
        
        # Calculate final values
        final_etf_low = etf_values_low[-1] if etf_values_low else initial_etf_balance
        final_etf_med = etf_values_med[-1] if etf_values_med else initial_etf_balance
        final_etf_high = etf_values_high[-1] if etf_values_high else initial_etf_balance
        
        return {
            'months_to_debt_free': months_to_debt_free if months_to_debt_free < max_months else None,
            'total_interest_paid': total_interest,
            'total_debt_payments': total_debt_payments,
            'total_etf_contributions': total_etf_contributions,
            'final_etf_value_low': final_etf_low,
            'final_etf_value_medium': final_etf_med,
            'final_etf_value_high': final_etf_high,
            'debt_snapshots': debt_snapshots,
            'etf_values_low': etf_values_low,
            'etf_values_medium': etf_values_med,
            'etf_values_high': etf_values_high,
        }
    
    def create_scenario_comparison(
        self,
        scenario_name: str,
        monthly_extra_debt: float,
        monthly_etf: float,
        strategy: PayoffStrategy,
        annual_return_low: float,
        annual_return_med: float,
        annual_return_high: float,
        initial_etf_balance: float = 0.0,
        description: str = ""
    ) -> ScenarioComparison:
        """
        Create a scenario comparison object.
        
        Args:
            scenario_name: Name of the scenario
            monthly_extra_debt: Extra monthly debt payment
            monthly_etf: Monthly ETF contribution
            strategy: Debt payoff strategy
            annual_return_low: Low annual return estimate
            annual_return_med: Medium annual return estimate
            annual_return_high: High annual return estimate
            initial_etf_balance: Starting ETF balance
            description: Scenario description
        
        Returns:
            ScenarioComparison object
        """
        results = self.simulate_combined_scenario(
            monthly_extra_debt,
            monthly_etf,
            strategy,
            annual_return_low,
            annual_return_med,
            annual_return_high,
            initial_etf_balance
        )
        
        # Calculate net worth (ETF value - remaining debt)
        # At end of simulation, debt should be 0 if paid off
        remaining_debt = 0.0 if results['months_to_debt_free'] else self.debts.total_balance()
        
        return ScenarioComparison(
            scenario_name=scenario_name,
            months_to_debt_free=results['months_to_debt_free'],
            total_interest_paid=results['total_interest_paid'],
            total_debt_payments=results['total_debt_payments'],
            total_etf_contributions=results['total_etf_contributions'],
            estimated_etf_value_low=results['final_etf_value_low'],
            estimated_etf_value_medium=results['final_etf_value_medium'],
            estimated_etf_value_high=results['final_etf_value_high'],
            net_worth_at_end_low=results['final_etf_value_low'] - remaining_debt,
            net_worth_at_end_medium=results['final_etf_value_medium'] - remaining_debt,
            net_worth_at_end_high=results['final_etf_value_high'] - remaining_debt,
            description=description
        )
    
    def compare_scenarios(
        self,
        monthly_surplus: float,
        strategy: PayoffStrategy,
        annual_return_low: float,
        annual_return_med: float,
        annual_return_high: float,
        initial_etf_balance: float = 0.0
    ) -> Tuple[ScenarioComparison, ScenarioComparison, ScenarioComparison]:
        """
        Compare three standard scenarios.
        
        Args:
            monthly_surplus: Available monthly surplus
            strategy: Debt payoff strategy
            annual_return_low: Low annual return estimate
            annual_return_med: Medium annual return estimate
            annual_return_high: High annual return estimate
            initial_etf_balance: Starting ETF balance
        
        Returns:
            Tuple of (minimum_only, debt_only, balanced) scenarios
        """
        # Scenario 1: Minimum payments only (no extra)
        minimum_only = self.create_scenario_comparison(
            scenario_name="Minimum Payments Only",
            monthly_extra_debt=0.0,
            monthly_etf=0.0,
            strategy=strategy,
            annual_return_low=annual_return_low,
            annual_return_med=annual_return_med,
            annual_return_high=annual_return_high,
            initial_etf_balance=initial_etf_balance,
            description="Pay only minimum payments on all debts with no extra allocation."
        )
        
        # Scenario 2: 100% to debt
        debt_only = self.create_scenario_comparison(
            scenario_name="100% Debt Payoff",
            monthly_extra_debt=monthly_surplus,
            monthly_etf=0.0,
            strategy=strategy,
            annual_return_low=annual_return_low,
            annual_return_med=annual_return_med,
            annual_return_high=annual_return_high,
            initial_etf_balance=initial_etf_balance,
            description="Allocate 100% of surplus to extra debt payments."
        )
        
        # Scenario 3: 70/30 split (balanced)
        balanced = self.create_scenario_comparison(
            scenario_name="Balanced (70% Debt / 30% ETF)",
            monthly_extra_debt=monthly_surplus * 0.7,
            monthly_etf=monthly_surplus * 0.3,
            strategy=strategy,
            annual_return_low=annual_return_low,
            annual_return_med=annual_return_med,
            annual_return_high=annual_return_high,
            initial_etf_balance=initial_etf_balance,
            description="Allocate 70% of surplus to debt and 30% to ETF investing."
        )
        
        return minimum_only, debt_only, balanced
