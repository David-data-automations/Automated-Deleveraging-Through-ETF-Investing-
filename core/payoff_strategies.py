"""
Payoff Strategies Engine

Implements different debt payoff strategies (avalanche, snowball, hybrid).
"""

from typing import List, Tuple, Optional
from data_models import Debt, DebtPortfolio, PayoffStrategy
import copy


class PayoffStrategyEngine:
    """Manages different debt payoff strategies."""
    
    @staticmethod
    def prioritize_debts(
        debts: List[Debt],
        strategy: PayoffStrategy,
        hybrid_balance_threshold: float = 1000.0
    ) -> List[Debt]:
        """
        Prioritize debts according to the specified strategy.
        
        Args:
            debts: List of debts to prioritize
            strategy: Payoff strategy to use
            hybrid_balance_threshold: For hybrid strategy, balance threshold
                                     below which to use snowball
        
        Returns:
            List of debts in priority order (highest priority first)
        """
        # Filter out paid-off debts
        active_debts = [d for d in debts if d.current_balance > 0]
        
        if strategy == PayoffStrategy.AVALANCHE:
            # Highest interest rate first
            return sorted(
                active_debts,
                key=lambda d: (-d.annual_interest_rate, d.current_balance)
            )
        
        elif strategy == PayoffStrategy.SNOWBALL:
            # Smallest balance first
            return sorted(
                active_debts,
                key=lambda d: (d.current_balance, -d.annual_interest_rate)
            )
        
        elif strategy == PayoffStrategy.HYBRID:
            # Small balances first (snowball), then high interest (avalanche)
            small_debts = [d for d in active_debts if d.current_balance <= hybrid_balance_threshold]
            large_debts = [d for d in active_debts if d.current_balance > hybrid_balance_threshold]
            
            # Sort small debts by balance (snowball)
            small_sorted = sorted(
                small_debts,
                key=lambda d: (d.current_balance, -d.annual_interest_rate)
            )
            
            # Sort large debts by interest rate (avalanche)
            large_sorted = sorted(
                large_debts,
                key=lambda d: (-d.annual_interest_rate, d.current_balance)
            )
            
            # Small debts first, then large debts
            return small_sorted + large_sorted
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    @staticmethod
    def allocate_extra_payment(
        debts: List[Debt],
        extra_payment: float,
        strategy: PayoffStrategy
    ) -> List[Tuple[Debt, float]]:
        """
        Allocate extra payment across debts according to strategy.
        
        Args:
            debts: List of debts
            extra_payment: Extra amount to allocate beyond minimums
            strategy: Payoff strategy to use
        
        Returns:
            List of tuples: (debt, extra_payment_amount)
        """
        if extra_payment <= 0:
            return [(debt, 0.0) for debt in debts]
        
        # Prioritize debts
        prioritized = PayoffStrategyEngine.prioritize_debts(debts, strategy)
        
        allocations = []
        remaining = extra_payment
        
        for debt in prioritized:
            if remaining <= 0:
                allocations.append((debt, 0.0))
                continue
            
            # Allocate all remaining extra payment to highest priority debt
            # (waterfall method - pay off one at a time)
            max_needed = debt.current_balance - debt.principal_in_minimum()
            allocation = min(remaining, max_needed)
            
            allocations.append((debt, allocation))
            remaining -= allocation
            
            # If this debt will be paid off, continue to next
            if allocation >= max_needed:
                continue
            else:
                # This debt gets all remaining, stop here
                break
        
        # Add zero allocations for any remaining debts
        allocated_debt_names = {debt.name for debt, _ in allocations}
        for debt in debts:
            if debt.name not in allocated_debt_names:
                allocations.append((debt, 0.0))
        
        return allocations
    
    @staticmethod
    def simulate_payoff(
        debts: List[Debt],
        monthly_extra_payment: float,
        strategy: PayoffStrategy,
        max_months: int = 600
    ) -> Tuple[List[dict], float, int]:
        """
        Simulate debt payoff over time.
        
        Args:
            debts: List of debts
            monthly_extra_payment: Extra payment beyond minimums each month
            strategy: Payoff strategy to use
            max_months: Maximum months to simulate
        
        Returns:
            Tuple of:
            - List of monthly snapshots (dicts with debt states)
            - Total interest paid
            - Months to debt-free (or max_months if not paid off)
        """
        # Create working copies of debts
        working_debts = [copy.deepcopy(debt) for debt in debts]
        
        monthly_snapshots = []
        total_interest_paid = 0.0
        months_to_debt_free = max_months
        
        for month in range(1, max_months + 1):
            # Check if all debts are paid off
            if all(d.current_balance <= 0 for d in working_debts):
                months_to_debt_free = month - 1
                break
            
            # Calculate this month's allocation
            allocations = PayoffStrategyEngine.allocate_extra_payment(
                working_debts,
                monthly_extra_payment,
                strategy
            )
            
            month_snapshot = {
                'month': month,
                'debts': [],
                'total_payment': 0.0,
                'total_interest': 0.0,
                'total_principal': 0.0,
                'total_remaining': 0.0,
            }
            
            # Process each debt
            for debt in working_debts:
                if debt.current_balance <= 0:
                    continue
                
                # Find extra allocation for this debt
                extra = next((amt for d, amt in allocations if d.name == debt.name), 0.0)
                
                # Calculate payment components
                interest = debt.interest_this_month()
                total_payment = debt.minimum_payment + extra
                principal = total_payment - interest
                
                # Don't overpay
                principal = min(principal, debt.current_balance)
                total_payment = interest + principal
                
                # Update balance
                debt.current_balance -= principal
                debt.current_balance = max(0, debt.current_balance)
                
                # Record
                total_interest_paid += interest
                
                month_snapshot['debts'].append({
                    'name': debt.name,
                    'payment': total_payment,
                    'interest': interest,
                    'principal': principal,
                    'remaining_balance': debt.current_balance,
                })
                
                month_snapshot['total_payment'] += total_payment
                month_snapshot['total_interest'] += interest
                month_snapshot['total_principal'] += principal
                month_snapshot['total_remaining'] += debt.current_balance
            
            monthly_snapshots.append(month_snapshot)
        
        return monthly_snapshots, total_interest_paid, months_to_debt_free
    
    @staticmethod
    def calculate_interest_saved(
        debts: List[Debt],
        monthly_extra_payment: float,
        strategy: PayoffStrategy
    ) -> Tuple[float, float]:
        """
        Calculate interest saved vs minimum-only payments.
        
        Args:
            debts: List of debts
            monthly_extra_payment: Extra payment beyond minimums
            strategy: Payoff strategy to use
        
        Returns:
            Tuple of (interest_with_extra, interest_minimum_only)
        """
        # Simulate with extra payments
        _, interest_with_extra, _ = PayoffStrategyEngine.simulate_payoff(
            debts,
            monthly_extra_payment,
            strategy
        )
        
        # Simulate minimum-only
        _, interest_minimum_only, _ = PayoffStrategyEngine.simulate_payoff(
            debts,
            0.0,
            strategy
        )
        
        return interest_with_extra, interest_minimum_only
    
    @staticmethod
    def get_strategy_description(strategy: PayoffStrategy) -> str:
        """
        Get human-readable description of strategy.
        
        Args:
            strategy: Payoff strategy
        
        Returns:
            Description string
        """
        descriptions = {
            PayoffStrategy.AVALANCHE: (
                "Avalanche Method: Prioritizes debts with the highest interest rates first. "
                "This approach minimizes total interest paid and is mathematically optimal."
            ),
            PayoffStrategy.SNOWBALL: (
                "Snowball Method: Prioritizes debts with the smallest balances first. "
                "This approach provides psychological wins through quick payoffs, "
                "which can help maintain motivation."
            ),
            PayoffStrategy.HYBRID: (
                "Hybrid Method: Combines snowball and avalanche approaches. "
                "Pays off small debts first for quick wins, then tackles high-interest debts. "
                "Balances psychological benefits with interest savings."
            ),
        }
        return descriptions.get(strategy, "Unknown strategy")
