"""
Core Package

Contains all core logic for debt deleveraging planning.
"""

from .planner import DeleveragingPlanner
from .cashflow import CashflowAnalyzer, calculate_amortization_schedule, calculate_total_interest
from .etf_allocation import ETFAllocationEngine
from .simulation import SimulationEngine
from .payoff_strategies import PayoffStrategyEngine
from .explanations import NarrativeGenerator

__all__ = [
    'DeleveragingPlanner',
    'CashflowAnalyzer',
    'ETFAllocationEngine',
    'SimulationEngine',
    'PayoffStrategyEngine',
    'NarrativeGenerator',
    'calculate_amortization_schedule',
    'calculate_total_interest',
]
